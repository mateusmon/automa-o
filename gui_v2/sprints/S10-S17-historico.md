## Sprint 10 — concorrência e pausa

- [x] **Gate Sol G10 — contratos de isolamento e concorrência definidos após auditoria da
  GUI, da Sentinela e dos artefatos da suíte.**

  **Diagnóstico que impede paralelismo imediato:**

  - `SentinelController`, `SentinelExecutionService` e `ProcessSupervisor` representam hoje uma
    única execução mutável. A fila, a saída, o estado de parada e os artefatos não podem ser
    compartilhados por dois processos.
  - `sentinela/storage.py` identifica o run apenas até o minuto; duas jornadas do mesmo cliente
    podem escrever no mesmo diretório e no mesmo `report.html`.
  - Trace e evidência possuem temporários isolados, mas os diretórios finais usam timestamp até
    o segundo. `sentinela/executor.py` procura o artefato por nome e `mtime` em raízes globais;
    duas execuções simultâneas do mesmo teste podem capturar ou mover o arquivo uma da outra.
  - `utils/logging_manager.py` grava por data e nodeid; o mesmo teste simultâneo compartilha o
    arquivo. O histórico por cliente já usa `FileLock` e escrita atômica, mas a ordem de chegada
    continua sendo “último encerramento vence” e deve ser documentada, não inferida pela UI.

  **Identidade, propriedade e estado:**

  - Cada clique aceito em Iniciar cria um `execution_id` opaco e único (UUID), antes do processo,
    e captura um snapshot imutável de cliente, modo, alvo, `count`, TTL e opções. O identificador
    atravessa GUI, CLI da Sentinela e subprocessos Pytest por argumento/variável dedicada; não é
    derivado de PID, horário, índice visual ou nome do módulo.
  - Introduzir um registro sem widgets por execução contendo identidade, snapshot, estado, fila,
    supervisor exclusivo, timestamps, saída e artefatos. Eventos carregam `execution_id`; evento
    tardio só pode atualizar o registro dono. A página recebe projeções prontas do controlador.
  - Cada processo raiz da Sentinela pertence a exatamente um `ProcessSupervisor`/Job Object.
    Parar uma execução atua somente nesse dono. “Parar todas”, se adicionado, apenas itera pelos
    registros conhecidos; nunca procura ou encerra Python/Chromium globalmente.
  - Estados válidos por registro: `STARTING`, `RUNNING`, `PAUSE_REQUESTED`, `PAUSED_BETWEEN_TESTS`,
    `STOPPING` e um estado terminal. Vaga de paralelismo só é liberada depois de processo, pipes
    e evento final terminarem; uma execução pausada continua ocupando vaga.

  **Diretórios e artefatos:**

  - Cada run usa uma pasta exclusiva sob `sentinela/reports`, com timestamp até segundos e um
    fragmento do `execution_id`; a criação deve falhar em colisão, nunca reutilizar uma pasta.
    A CLI imprime uma linha inequívoca associando ID e pasta para a GUI validar.
  - Logs, evidências, traces e temporários produzidos pelo Pytest recebem uma raiz/namespace da
    execução. O executor procura e move artefatos somente dentro dessa raiz; fica proibida a
    busca global por “arquivo mais recente”. Relatório e traces continuam validados sob
    `sentinela/reports`, agora também contra o `execution_id` dono.
  - `configs.local.yaml` permanece fora do caminho concorrente: cliente é passado por
    `ASI_CLIENTE_ATIVO`. Configuração, catálogo e `ordem.yaml` continuam somente leitura.
    Limpeza por TTL nunca remove a pasta de um registro ativo da GUI.

  **Limite, seleção e apresentação:**

  - S10.2 habilita exatamente duas jornadas da Sentinela no mesmo cliente, escolhidas antes de
    iniciar e executadas em paralelo. Duplicar o mesmo prefixo no mesmo lote é rejeitado. Pytest
    simples e Sentinela não se misturam nesta sprint; a exclusão atual entre as duas engines fica.
  - O lote não é um processo: é somente um agrupamento visual de execuções independentes.
    Cada card/linha mostra alvo, estado e ações próprias; selecionar um registro determina quais
    logs, relatório, pasta e traces são apresentados. Encerrar um não limpa o outro.
  - O limite é fixo e definitivo em 2 execuções simultâneas. Não implementar expansão, fila ou
    cancelamento de pendentes. O modo Jornada aceita duas jornadas distintas; o modo Teste
    específico aceita um ou dois arquivos distintos do catálogo para o mesmo cliente. Lote de
    dois testes específicos usa `count=1` e não combina multi-cliente. O registro valida a
    capacidade antes de criar qualquer processo.

  **Cancelamento e pausas:**

  - Cancelamento mantém a sequência validada: Ctrl+Break cooperativo, prazo e Job Object como
    fallback. Cancelar uma execução ativa não afeta
    irmãos. Fechar a GUI lista quantas execuções estão ativas, pede uma confirmação e
    aguarda todas chegarem ao terminal antes de destruir a janela.
  - Há dois comportamentos existentes de espera interativa e eles permanecem distintos. O Genesis
    legado roda pelo próprio `GenesisRunner` e exibe `MessageBoxW` síncrono ao terminar com
    sucesso ou falha; a execução só segue para o encerramento do navegador depois que o usuário
    fecha o popup. Na Sentinela/Pytest, `pytest_exception_interact` chama `page.pause()` antes do
    teardown: testes comuns só fazem isso quando `--pausa` ativa `ASI_PAUSAR_NA_FALHA=1`, enquanto
    `tests/genesis` sempre faz isso com navegador visível; headless nunca abre o Inspector. O
    usuário retoma esse segundo tipo pelo botão Resume do Inspector.
  - S10.5 implementa um terceiro comportamento, a pausa/continuação da sequência da Sentinela
    pela GUI v2, **somente na fronteira entre testes**. É diferente das pausas de inspeção por
    falha: não abre popup ou Inspector, não altera `--pausa`/`ASI_PAUSAR_NA_FALHA` e não muda a
    política do Genesis legado. Pedir pausa durante um teste deixa `PAUSE_REQUESTED`; o teste
    atual e suas retentativas terminam (incluindo eventual inspeção de falha no Inspector), então
    a Sentinela sinaliza `PAUSED_BETWEEN_TESTS` antes de iniciar o próximo e aguarda Continuar.
    Parar tem precedência sobre pausa. Enquanto `PAUSE_REQUESTED`, Continuar cancela o pedido
    pendente; após confirmação `PAUSED_BETWEEN_TESTS`, Continuar libera a próxima execução.
  - S10.6 é apenas pesquisa sobre suspensão manual genérica do navegador/Pytest durante operação
    ativa. Isso não se refere ao breakpoint atual do Playwright em falha. Não usar suspensão de
    processo/thread como atalho e não liberar a função sem protocolo de recuperação.

  **Sequência e gates:** S10.1 isola identidade e arquivos mantendo uma execução por vez;
  S10.2 habilita duas jornadas; S10.3 conclui a apresentação independente; S10.4 valida o teto de duas.
  Antes de S10.5, o Sol deve auditar a S10.1–S10.4 e definir o canal cooperativo de pausa. S10.6
  não tem autorização de implementação.

  **Arquivos previstos:** em S10.1, `gui_v2/models/execution.py`, um serviço/registro pequeno em
  `gui_v2/`, `services/process_supervisor.py`, `services/sentinel_command_service.py`,
  `services/sentinel_artifact_service.py`, `sentinela/sentinela.py`, `sentinela/runner.py`,
  `sentinela/executor.py`, `sentinela/storage.py`, `conftest.py` e os utilitários de log,
  evidência e trace. Alterar somente o necessário para propagar o ID e criar namespaces; não
  redesenhar a página nem habilitar concorrência em S10.1.

  **Verificação obrigatória de S10.1:** IDs distintos em partidas no mesmo segundo; pastas
  distintas para mesmo cliente/alvo; rejeição de colisão e ID inválido; eventos tardios não
  cruzam registros; artefato de uma execução não é localizado pela outra; cancelamento encerra
  somente o Job Object dono; compatibilidade da CLI sem ID explícito gera um ID seguro; nenhuma
  alteração em `configs.local.yaml`. Fazer primeiro testes sem navegador e depois uma jornada
  curta autorizada. Não executar dois browsers ainda.

  **Luna liberado somente para S10.1.** Ao concluí-la, parar para revisão do Sol antes de S10.2.

- [x] S10.1 — propagar identidade única e isolar diretórios/artefatos, preservando execução
  única na interface. A GUI registra snapshot imutável, estado, fila, supervisor e artefatos
  por UUID, propagado pela CLI ao Pytest. Runs exclusivos registram proprietário;
  logs/evidências/traces usam namespace e o executor busca somente nessa raiz. Eventos e
  artefatos são conferidos pelo ID; sete testes sem navegador passaram e a consulta
  de Material no CJF v4 passou. TSE v3 não validou por senha expirada no login. Hash de
  `configs.local.yaml` permaneceu igual.
- [x] S10.2 — permitir duas jornadas distintas no mesmo cliente, cada uma com processo e estado
  próprios. A Sentinela aceita exatamente duas seleções diferentes, pré-valida ambos os comandos
  antes de criar processos e inicia um supervisor, UUID, fila e snapshot por alvo. Cancelamento
  aceita ID individual ou todos (fechamento); eventos e saída ficam etiquetados por prefixo.
  Mantidos modo Teste específico e guarda Pytest/Sentinela. O fechamento para e aguarda as árvores
  conhecidas antes de destruir a janela. 15 testes sem navegador, compilação e validação da
  montagem real de dois comandos no cliente ativo passaram; nenhuma execução de navegador em
  paralelo foi iniciada nesta etapa.
- [x] S10.3 — separar a apresentação por execução selecionada. A página ganhou seletor por alvo,
  estado e ID; saída, relatório, pasta e traces agora vêm do registro selecionado, sem misturar
  execuções irmãs nem perder o histórico ao trocar cliente/modo. Cada navegador continua em seu
  processo Sentinela independente. Compilação e smoke test lógico de seleção/artefatos passaram.
  Tcl/Tk 8.6.15 está instalado: o erro de inicialização observado era restrito ao sandbox;
  widgets reais validados com janela oculta pelo `.venv` fora do sandbox: troca de execução,
  isolamento dos logs/artefatos, preservação da escolha do trace durante atualização,
  rejeição de trace alheio e restauração da página. Não substitui inspeção visual do layout.
  **Nota de ambiente para próximas validações Tk:** usar `.venv\Scripts\python.exe` fora do
  sandbox; `init.tcl` e Tcl/Tk 8.6.15 já estão instalados, e o sandbox causa o falso erro de
  inicialização. Solicitar execução autorizada fora do sandbox em vez de baixar/reinstalar Tcl/Tk.
  Revisão visual antes do commit da S10: o polling de 100 ms chamava `set_running()` e recriava
  todas as linhas de jornadas mesmo sem mudança de estado, causando o piscar registrado em vídeo.
  O redesenho da árvore agora ocorre só na transição entre parado e em execução; textos e botões
  estáveis deixam de ser reconfigurados a cada ciclo. Em widgets Tk reais, 50 atualizações
  consecutivas preservaram as mesmas linhas, e a transição para parado atualizou a árvore.
- [x] S10.4 — medir e validar o limite definitivo de duas execuções. `ProcessSupervisor` mede
  cada Job Object no Windows: CPU por intervalo, working set agregado, processos ativos e
  processos de navegador (incluindo `chrome-headless-shell.exe`, não janelas). O painel mostra
  a amostra da execução selecionada e conserva a última amostra disponível ao terminar. O modo Teste específico permite selecionar até
  dois arquivos catalogados distintos para o mesmo cliente; ambos são revalidados antes do
  início. Lote de dois não admite repetição nem multi-cliente. Pytest cache provider fica
  desabilitado somente nos processos iniciados pela Sentinela da GUI v2 para evitar colisão em
  `.pytest_cache`. Widgets Tk reais selecionaram dois, recusaram um terceiro e exibiram as
  métricas. Duas árvores Chromium simultâneas em Job Objects diferentes mediram, cada uma, 7
  processos, 4 processos de navegador e ~290–291 MiB, terminando com código 0. Duas consultas reais também
  iniciaram simultaneamente: cada Job chegou a 9 processos e ~345–376 MiB; ambas falharam antes
  do login porque o endpoint JFRJ ativo responde HTTP 404 (`/jfrj-migra40/`). O primeiro ensaio
  revelou a colisão de `.pytest_cache`, corrigida acima. Nenhuma alteração na URL, configuração
  local, Sentinela, `conftest.py` ou engines. Compilação e hash da configuração verificados.
  Revisão final: registro aceita o par de testes; fechamento do Job ocorre antes do evento
  terminal, sem timer atrasado. Cancelar uma árvore Chromium preservou a irmã e a reutilização
  do supervisor passou. Relatório com falha produz FAILED mesmo com exit code zero; relatório
  ausente/inválido não é anunciado como sucesso. Artefatos exigem identidade do run validada.
  Saída dos filhos usa UTF-8; seleção específica é restaurada ao recriar a página.
  Teto mantido exatamente em 2, sem expansão futura.
- [x] **Gate Sol G10-P — auditoria e contrato de pausa cooperativa para S10.5.**

  **Auditoria S10.1–S10.4:**

  - `ExecutionRegistry` mantém até duas execuções registradas, cada uma com UUID, snapshot,
    fila, supervisor e estado próprios. O supervisor fecha seu Job Object antes de publicar
    `PROCESS_EXITED`; o controlador descarta eventos cujo `execution_id` não corresponde ao
    registro consumidor. `PAUSED_BETWEEN_TESTS` ainda não existe no modelo nem na contagem de
    vagas e deverá ser tratado como estado ativo.
  - `SentinelController.stop(execution_id)` já direciona o cancelamento ao supervisor dono;
    o fechamento pode parar as execuções conhecidas. S10.5 deve preservar essa propriedade e
    fazer Stop vencer qualquer pedido de pausa ou continuação pendente.
  - A CLI recebe `--execution-id`; `runner` propaga a identidade ao `executor`, que cria um
    processo Pytest separado por teste e injeta `ASI_EXECUTION_ID`. Diretórios de run, logs,
    evidências e traces já têm namespace. A comunicação de pausa deve carregar o mesmo UUID;
    nenhum arquivo/canal compartilhado sem validação de proprietário é aceitável.
  - `conftest.py` já lê variáveis específicas da execução e possui hooks de início/fim de teste;
    a Sentinela controla a sequência e as retentativas. Assim, o ponto de espera é o laço
    externo do runner, depois de concluir todas as tentativas do alvo corrente e antes de iniciar
    o próximo processo Pytest. Não suspender o Pytest, navegador, thread ou processo ativo.

  **Contrato de S10.5 (escopo liberado):**

  - Preservar a separação entre as pausas: o popup bloqueante do Genesis legado continua sob seu
    runner; o `page.pause()` existente continua sendo controlado pela política de falha do
    `conftest.py` (`--pausa` para testes comuns, sempre para `tests/genesis` visível, nunca
    headless); os controles Pausar/Continuar da GUI v2 atuam somente sobre a sequência da
    Sentinela entre processos Pytest. Se o usuário retomar o Inspector após uma falha com pausa
    da GUI pendente, a Sentinela conclui as retentativas daquele teste e só então aplica sua
    pausa na próxima fronteira.
  - O canal é um arquivo JSON `.gui-control-<execution_id>.json` diretamente em
    `sentinela/reports`, exclusivo pela identidade e validado contra a pasta do run ativo. A raiz
    é necessária porque o modo multi-cliente cria várias pastas de run sob um único registro da
    GUI. A Sentinela relê o comando antes de cada item do laço externo de jornada/repetição. O
    conteúdo leva versão de schema, ID e comando fechado (`pause`, `resume`, `stop`), é escrito
    atomicamente pela GUI e recusado se ID, caminho ou conteúdo não corresponderem ao registro
    dono. Ausência/arquivo parcial não pode iniciar pausa nem derrubar a execução. `stop` é
    terminal no canal e não pode ser sobrescrito por `resume`; o arquivo é removido ao finalizar
    o processo dono.
  - Pausar durante teste grava `pause` e mantém estado `PAUSE_REQUESTED`; as tentativas do teste
    atual terminam. Antes do próximo teste, a Sentinela publica um marcador inequívoco com ID e
    aguarda `resume`. Enquanto aguarda, estado `PAUSED_BETWEEN_TESTS` ocupa vaga e mantém vivos
    o processo e seu supervisor. `resume` libera somente o mesmo ID. Se a pausa for pedida
    durante o último teste, a execução termina normalmente porque não existe próxima fronteira.
  - Stop grava `stop`/aciona o cancelamento dono e tem precedência sobre pause/resume, inclusive
    se o comando chegar junto à fronteira. Fechamento da GUI continua usando o cancelamento
    validado e aguardando os processos conhecidos; pausadas contam como ativas.
  - A interface oferece Pausar/Continuar para a execução selecionada, apresenta os estados
    acima por registro e não converte pausa em sucesso/falha terminal. Com dois processos, o
    comando afeta somente o registro selecionado.
  - Arquivos previstos: `models/execution.py`, `services/execution_registry.py`,
    `controllers/sentinel_controller.py`, `pages/sentinel_page.py`, `sentinela/sentinela.py`,
    `sentinela/runner.py` e `sentinela/storage.py`; tocar `executor.py`/supervisor somente se a
    auditoria demonstrar necessidade. Não alterar Pytest, navegador, sessão ASI, GUI antiga,
    configurações ou política de artefatos.

  **Verificação esperada antes de uso real:** testes sem UI para arquivo ausente/parcial,
  comandos inválidos, isolamento de IDs, pausa antes da fronteira, pausa enquanto teste está
  ativo, retomada, Stop durante espera e Stop concorrente com Resume; confirmar que não começa
  o próximo teste antes de Resume e que a capacidade continua ocupada. Depois, validar uma
  jornada curta autorizada com pausa entre testes e cancelamento seguro. Não pausar no meio de
  operação nem iniciar pausa simultânea em dois browsers nesta microsprint.

  **Luna liberado para S10.5 somente.**
- [x] S10.5 — pausa e continuação cooperativas somente entre testes. Os controles JSON por ID
  validam run, proprietário, schema e comandos; gravações concorrentes são serializadas para
  que `resume` nunca sobrescreva `stop` (25 corridas simultâneas passaram). Testes sem navegador
  confirmaram ausência/JSON parcial, isolamento de IDs, capacidade ocupada durante pausa,
  retomada somente após `resume`, Stop durante a espera e callback da GUI restrita à execução
  selecionada. No TRE-PE, duas Consultas de Material passaram; uma pausa solicitada durante a
  primeira só liberou a segunda após `resume`. Stop durante outra pausa encerrou antes da
  segunda consulta, sem browser ou processo Pytest ativo. A parada Windows terminou por
  Ctrl+Break (código `3221225786`); o marcador de PID restante é ignorado pela limpeza TTL
  quando o processo já não existe. A limpeza explícita também preserva qualquer run com PID
  proprietário ativo. Compilação dos arquivos alterados passou.
- [x] S10.6 — pesquisar pausa manual durante um teste ativo, sem implementar. O ambiente usa
  Playwright 1.57.0; [`browser_context.debugger.request_pause()`](https://playwright.dev/python/docs/api/class-debugger)
  só foi introduzido na 1.59 e pausa antes da próxima ação do Playwright. O objeto `BrowserContext`
  vive no processo/thread Pytest, e a [API não é thread-safe](https://playwright.dev/python/docs/library#threading):
  a GUI não deve chamá-la diretamente. A árvore Sentinela também separa GUI, runner, Pytest e
  Chromium; o canal S10.5 é consumido pelo runner, fora da chamada do teste. Uma varredura
  encontrou cerca de 1.918 chamadas diretas de ação/navegação em 578 arquivos Python, sem um
  ponto universal de interceptação.

  **Alternativa segura encontrada, sem alterar código ou elevar a dependência:** usar o modo
  oficial de depuração do Playwright, `PWDEBUG=1` (com execução interativa, por exemplo,
  `pytest -s`). O Inspector já permite pausar, avançar cada ação Playwright e continuar. Ele atua
  no processo/thread que possui a page; não suspende threads do Windows e não precisa da API nova
  da versão 1.59. Limites: é depuração manual iniciada antes da execução, força modo headed e
  timeout padrão zero; não é um botão de pausa genérico da GUI que possa ser acionado a qualquer
  momento. Para inspecionar uma falha configurada para pausar, o `page.pause()` existente
  continua sendo a opção direta.

  **Decisão:** não implementar checkpoints genéricos em centenas de flows nem atualizar Playwright
  para habilitar o debugger 1.59 enquanto o Inspector existente atende à depuração manual. Manter
  as três pausas com escopos distintos: modal do Genesis legado; Inspector por falha; pausa
  cooperativa da GUI entre testes. Qualquer futuro botão de pausa durante o teste exige requisito
  concreto que o Inspector não atenda, seguido de gate para cobertura, sessão ASI, operação
  pendente, headless, Stop/fechamento e recuperação com uma e duas execuções.

## Sprint 11 — distribuição e adoção

- [x] **Gate Sol G11 — estratégia de distribuição e adoção definida.**

  **Decisão de empacotamento e runtime:**

  - A entrega será uma pasta versionada e autocontida para Windows x64, não um executável
    PyInstaller/Nuitka. A aplicação abre Pytest, Sentinela, Codegen e Trace Viewer por
    `sys.executable`, importa testes/flows dinamicamente e lê YAMLs pelo filesystem; congelar só
    a GUI quebraria esse contrato ou exigiria um segundo runtime de qualquer forma.
  - Cada versão contém a árvore necessária do projeto, um Python 3.14 x64 privado e completo
    (incluindo Tcl/Tk, `python.exe` e `pythonw.exe`), as dependências exatas de
    `requirements.txt` e somente os browsers Chromium exigidos pelo Playwright fixado. Não usar
    o pacote embutível oficial do Python: ele não inclui Tcl/Tk nem `pip`, e a GUI depende de Tk.
  - O Chromium fica dentro da versão, em diretório explícito, e o lançador define
    `PLAYWRIGHT_BROWSERS_PATH` antes de abrir a GUI. Essa variável é herdada por Pytest,
    Sentinela, Codegen e Trace Viewer. Não depender do cache global do perfil do Windows nem
    baixar navegador na primeira execução do usuário.
  - O artefato de release é um ZIP com `manifest.json` e um sidecar SHA-256 publicado ao lado.
    O manifesto registra versão da aplicação, revisão de origem, Python, Playwright, Pytest,
    CustomTkinter e browser. O sidecar valida o ZIP final; build e instalação falham se qualquer
    item obrigatório ou versão divergir, sem atualização parcial de pacotes no computador do usuário.

  **Layout e lançamento:**

  - Instalação por usuário, sem privilégios administrativos, sob
    `%LOCALAPPDATA%\ASI Automacao\versions\<versao>`. Um diretório estável
    `%LOCALAPPDATA%\ASI Automacao\launcher` guarda o lançador e um pequeno arquivo de versão
    ativa; ele resolve a pasta, configura ambiente/cwd e chama o `pythonw.exe` privado com
    `-m gui_v2.main`. Caminhos com espaços e nomes de usuário não ASCII são obrigatórios.
  - Versões são imutáveis quanto a código/runtime, mas os diretórios de saída já esperados pelo
    projeto continuam graváveis dentro da versão durante esta sprint. Não redirecionar logs,
    evidências, traces, relatórios ou configuração por conveniência em S11.1; separar dados é
    uma decisão posterior e exige novo gate porque hoje vários módulos resolvem a raiz por
    `__file__`.
  - A GUI v2 recebe lançador próprio. `app.bat`, `app.vbs` e a GUI antiga não são substituídos,
    removidos nem redirecionados antes de S11.6. A distribuição pode conter a GUI antiga para
    suporte, mas o piloto deve usar atalhos com nomes inequívocos.

  **Atualização sem SVN e rollback:**

  - Usuários não instalam TortoiseSVN, Python, dependências ou browsers e não recebem working
    copy. O canal inicial é um diretório interno/UNC aprovado contendo o manifesto, ZIP e SHA-256;
    o endereço é configuração do instalador/piloto, nunca credencial ou caminho fixo no código.
    Um adaptador HTTPS poderá ser adicionado depois sem mudar o formato do release.
  - A atualização baixa/copia para arquivo temporário, valida hash e manifesto, extrai em staging,
    executa o smoke test e só então publica a nova pasta e troca atomicamente a versão ativa.
    Falha antes da troca preserva a versão atual. Não sobrescrever uma versão em uso e não apagar
    a anterior durante a atualização.
  - Rollback troca o ponteiro para a versão anterior já validada. Manter pelo menos a versão ativa
    e uma anterior; limpeza de versões mais antigas só ocorre quando nenhuma execução as usa.
    O rollback não converte arquivos produzidos por uma versão mais nova.

  **Preferências e estado local:**

  - Em S11.3, antes da ativação, copiar para staging somente
    `gui_v2/preferences.local.json` e `configs/configs.local.yaml` da versão ativa, por lista
    explícita. Validar o `schema_version` das preferências; versão incompatível usa padrões e
    preserva o original para retorno. Nunca copiar temporários, logs, evidências, traces,
    relatórios, cache ou credenciais de outra fonte.
  - A versão anterior permanece intacta, portanto rollback também restaura suas preferências.
    Migrações futuras são de avanço, idempotentes e nunca alteram retroativamente a pasta antiga.

  **Ordem de adoção e limites:**

  - S11.1 produz somente o pacote autocontido e um lançador de validação. Não cria atualizador,
    atalho definitivo, instalador com elevação, telemetria, assinatura de código ou troca da GUI
    padrão. Os arquivos novos ficam sob `gui_v2/distribution/`; engines e GUI antiga permanecem
    somente leitura.
  - S11.2 adiciona instalação lado a lado e atualização pelo canal interno; S11.3 adiciona
    migração/rollback; S11.4 faz piloto pequeno mantendo a GUI antiga disponível; S11.5 executa
    regressão; S11.6 exige aceite explícito para trocar o lançador padrão ou aposentar algo.
  - O piloto começa em uma máquina limpa sem Python/SVN e uma máquina já usada, primeiro com
    consulta curta em um cliente autorizado. Expansão depende de GUI, execução normal,
    Sentinela, pausa/cancelamento, Codegen, Trace Viewer e rollback aprovados.

  **Arquivos previstos para S11.1:** `gui_v2/distribution/build_release.ps1`, manifesto/template
  e lançador de validação dentro da mesma pasta. O script recebe caminhos explícitos para a
  distribuição completa do Python e para a saída, monta staging novo, instala dependências e
  Chromium nele e gera ZIP/hash; não modifica `.venv`, checkout, caches globais ou arquivos do
  usuário. Dependências de build não entram em `requirements.txt` de runtime.

  **Verificação obrigatória de S11.1:** compilar os módulos Python; inspecionar o manifesto;
  confirmar hash sobre o ZIP final; extrair em caminho com espaços; iniciar a GUI v2 com o
  runtime privado; confirmar Tcl/Tk, imports e browser local; montar sem executar os comandos de
  Pytest/Sentinela/Codegen/Trace Viewer e verificar que todos apontam para o Python privado e
  herdam o browser local. Depois executar somente um smoke curto autorizado. Repetir sem Python,
  Playwright ou SVN disponíveis no `PATH`.

  **Luna liberado somente para S11.1.** Ao concluí-la, parar para revisão antes de S11.2.

- [~] S11.1 — empacotamento, runtime e browser. Suspensa a pedido do usuário; retomar
  quando a GUI v2 estiver satisfatória e o empacotamento voltar a ser prioridade.
- [ ] S11.2 — atualização sem SVN para usuários.
- [ ] S11.3 — preferências e rollback.
- [ ] S11.4 — piloto.
- [ ] S11.5 — regressão e aceite.
- [ ] S11.6 — decidir lançador padrão/destino da GUI antiga.

## Sprint 12 — histórico do último resultado por cliente

A pedido do usuário, esta trilha de refinamento avança antes da distribuição da Sprint 11,
que permanece suspensa. Lê `historico_testes/estado_atual/<cliente>.json` somente para exibição.
Seguir a agregação da GUI legada: remover `::nome_do_teste` para agrupar por arquivo e, quando
houver várias entradas, escolher a maior severidade (`fail > skip > pass`).

- [x] S12.1 — `HistoryService` lê o JSON do cliente em modo somente leitura e retorna histórico
  vazio para cliente ausente, arquivo ausente, JSON malformado ou estrutura incompatível. O
  caminho resolvido precisa permanecer diretamente sob `historico_testes/estado_atual`, incluindo
  proteção contra chaves de cliente que escapem da pasta e links simbólicos externos.
- [x] S12.2 — `HistoryService.aggregate_by_test_path()` remove o sufixo `::nome_do_teste`,
  agrupa entradas pelo path do arquivo e mantém o resultado de maior severidade
  (`fail > skip > pass`), seguindo a regra da GUI legada. Entradas empatadas preservam a última
  ocorrência do JSON; a etapa não conecta a agregação à interface.
- [x] S12.3 — o catálogo mostra antes do nome os indicadores de passou (✔ verde), falhou
  (✖ vermelho), skip (⚠ laranja) e sem histórico (• cinza). O controlador carrega o histórico
  do cliente inicial e envia somente os estados agregados por path; ao trocar de cliente, limpa
  os indicadores antigos para evitar exibir resultados de outro cliente. A recarga do novo
  cliente fica para S12.4.
- [x] S12.4 — recarrega o histórico ao trocar de cliente e após execuções terminais
  (sucesso, falha ou skip). Atualiza os indicadores existentes sem remontar o catálogo, mantendo
  seleção, pesquisa e posição de rolagem; execução interrompida não provoca recarga.
- [x] S12.5 — validação isolada confirmou resultados com múltiplos nodeids por arquivo,
  precedência (`fail > skip > pass`), desempate pela última entrada, histórico ausente,
  JSON corrompido e schema incompatível. Widgets reais no `.venv` confirmaram os indicadores
  e a atualização sem perda de pesquisa, seleção, identidade dos labels ou posição de rolagem.

## Microsprint final — aposentadoria do Genesis legado

- [x] Migração do Genesis concluída e funcional, conforme confirmação do usuário. Removidos o
  item Genesis do menu, a rota/modal placeholder e `pages/genesis_page.py`; a jornada Genesis
  integrada à Sentinela permanece intacta.

## Próxima micro-sprint

**Gate Sol G16 — diagnosticar a estabilidade visual ao redimensionar/restaurar.** Reproduzir
o quadro preto, localizar os contêineres envolvidos e propor a correção mínima antes de
implementar. Parar para decisão antes da implementação da Sprint 16.

## Sprint 13 — identidade visual configurável

Planejada para depois das sprints numeradas e da microsprint final, ao fim da fila atual.
Suavizar o vermelho forte usado nas páginas comuns e permitir que o usuário escolha a cor
predominante nas Configurações. A identidade da Sentinela permanece própria, mas acompanha o
preset selecionado.

- [x] **Gate Sol G13 — contrato de cores e preferências definido.**

  **Papéis dos tokens:** `accent_fill`, `accent_hover` e `accent_text` são a cor predominante
  selecionável nas páginas Execução e Configurações e no menu quando uma delas está ativa.
  `sentinel_fill`, `sentinel_hover` e `sentinel_text` acompanham o preset selecionado na
  página Sentinela, cabeçalho, menu e ícones de navegação, preservando a identidade visual
  própria da página sem fixá-la em vermelho. O logotipo ASI acompanha o destaque da página
  ativa. `success`, `warning` e `error` representam apenas resultados; falha no catálogo,
  estados de execução e botão de interrupção usam `error`, nunca `accent_fill`.
  Cores próprias dos módulos (Almoxarifado, Patrimônio, Corporativo) continuam independentes
  da preferência, com pares de texto/estado ajustados se o contraste exigir.

  **Paleta inicial fechada** (`accent_id` persistido; `vermelho_suave` é o padrão). Cada linha
  define preenchimento/hover no claro, preenchimento/hover no escuro e texto de destaque no
  escuro. No claro, o texto de destaque usa o preenchimento claro. Texto sobre botões coloridos
  é branco em ambos os modos:

  | `accent_id` | Claro: fill / hover | Escuro: fill / hover | Texto no escuro |
  |---|---|---|---|
  | `vermelho_suave` | `#B83B44` / `#A32F39` | `#C44D55` / `#C74E56` | `#EE9299` |
  | `azul` | `#355FAD` / `#2A529B` | `#5274BE` / `#5475BC` | `#93B5F1` |
  | `verde` | `#176D67` / `#125D57` | `#308079` / `#348078` | `#75CFC4` |
  | `violeta` | `#6654A8` / `#594695` | `#7C64B9` / `#7F67BA` | `#BBA8F2` |

  **Semântica e contraste:** texto de sucesso/alerta/erro no claro usa respectivamente
  `#16734F`, `#9B4E00`, `#B42335`; no escuro, `#67C59B`, `#FFAD5C`, `#F4909C`.
  Preenchimento de botão destrutivo usa `#B42335` no claro e `#C44D55` no escuro, com texto
  branco. Exigir pelo menos 4,5:1 para texto normal, 3:1 para indicadores/controles e estados
  visuais contra o fundo adjacente, em Claro e Escuro; Sistema aplica a variante efetiva do SO
  e deve ser verificado nos dois estados. A medição dos quatro presets acima confirmou mínimo
  de 4,51:1 para branco sobre preenchimento/hover e 3,09:1 para preenchimento escuro contra
  `surface_alt=#232831` (o fundo escuro mais claro dos cartões). O fundo escuro do cartão foi
  ajustado um nível para que o vermelho Sentinela original tenha 3,03:1 nesse entorno. Destaque usado como texto no
  escuro tem no mínimo 7,16:1 contra `surface=#1C2028`. Foco/seleção terão contorno com pelo
  menos 3:1 contra o entorno, pois a diferença de tom no hover escuro é sutil. Adicionar
  contorno quando a borda do destaque tocar `surface_alt`.
  Ícones e cores de módulos ainda devem ser verificados nos widgets reais durante as microsprints.

  **Preferência e migração:** `GuiPreferences` ganha `accent_id: str = "vermelho_suave"` e
  `preferences.local.json` passa a `schema_version: 2`, mantendo as demais chaves existentes.
  Ao ler schema 1, preservar `theme`, `speed_ms`, `log_level`, `full_output` e
  `browser_visible` com as validações atuais e atribuir `vermelho_suave`; gravar schema 2 só
  no próximo salvamento do usuário, de forma atômica. Em schema 2, `accent_id` ausente ou
  desconhecido volta ao padrão sem apagar outros campos válidos. Schema desconhecido ou JSON
  inválido continua no padrão geral. A seleção em Configurações é uma lista de presets,
  sem entrada hexadecimal livre; isso limita as cores a pares de contraste medidos.

  **Luna liberado para a Sprint 13.**

- [x] S13.1 — componentes comuns usam os tokens vermelho suave; a Sentinela mantém o
  preenchimento `#D92929`, usa hover `#B91F1F` no claro e `#C44D55` no escuro e recebe
  texto/contorno apropriados ao tema. O menu e o
  logotipo acompanham a página ativa; estados de falha usam token próprio. O fundo escuro dos
  cartões mudou de `#242933` para `#232831` para manter contraste 3:1 com o vermelho da
  Sentinela e seus estados de hover. Página real e controles representativos foram verificados
  em Claro e Escuro.
- [x] S13.2 — adicionada a aba Temas com o seletor de aparência e os quatro presets do G13.
  O seletor de aparência fica somente em Configurações > Temas, sem faixa cinza escura. A
  escolha do preset atualiza nesta sessão as páginas comuns, Sentinela, cabeçalhos, menu,
  ícones e logotipo. Textos dos presets, Codegen e Executar testes ficam brancos sobre fundos
  de destaque. Ao escolher um preset, a aba Temas continua aberta. A aplicação real confirmou
  os quatro presets e a troca de modo; naquela etapa, a aparência já era salva e o preset de
  cor predominante ainda não, persistência concluída em S13.3.
- [x] S13.3 — `GuiPreferences.accent_id` foi adicionado e o schema local passou a 2. O schema 1
  continua legível sem gravação automática, preserva os outros campos válidos e usa o preset
  padrão; schema 2 trata preset ausente/inválido sem descartar os demais valores. A escolha
  agora é salva atomicamente e restaurada ao iniciar. Validação isolada cobriu migração,
  fallback, schema desconhecido, JSON inválido e rejeição de preset inválido; a GUI real
  confirmou carregamento, seleção, persistência, navegação nas três páginas e restauração após
  reabertura usando arquivo temporário, sem alterar as preferências locais do usuário.
- [x] S13.4 — o seletor “Nível dos logs” agora usa o `CTkComboBox` e o padrão visual dos
  seletores da Execução: campo e dropdown na superfície, botão discreto, borda e estados de
  hover. O teste com widgets reais em Claro e Escuro confirmou a aplicação das variantes,
  o dropdown legível e a manutenção do callback que atualiza a preferência.

## Sprint 14 — seletor de cliente unificado e pesquisável

Planejada para o fim da fila atual. A página Execução e a Sentinela devem usar o mesmo
componente de seleção, com a aparência já adotada na Execução e pesquisa efetiva para que
a lista continue prática à medida que novos clientes forem adicionados.

- [x] **Gate Sol G14 — contrato do seletor de cliente fechado.**

  **Fonte e identidade:** `ConfigurationService.load().clients` é a fonte única e preserva a
  ordem configurada. O componente recebe pares `(key, label)` dos controladores; nunca lê ou
  grava YAML. A chave, única e estável, identifica o cliente no callback. Os resultados exibem
  nome e chave, distinguindo nomes repetidos; nenhum resultado é resolvido de volta para uma
  chave por comparação de texto. Execução e Sentinela mantêm suas escolhas ativas nos seus
  controladores, como já ocorre, sem sincronização implícita entre páginas.

  **Componente e aparência:** extrair um único seletor em `gui_v2/components/`, com campo,
  borda, botão e cores equivalentes ao seletor da Execução em Claro e Escuro. Usar lista
  flutuante ancorada ao campo, rolável e limitada a cerca de dez resultados visíveis para
  listas extensas; ela não deve alterar a altura do formulário nem ficar recortada pelo
  contêiner da página. A API mínima recebe clientes, chave ativa e `on_selected(key)` e expõe
  atualização da chave ativa e bloqueio/desbloqueio. A página não guarda uma segunda fonte de
  verdade para a seleção.

  **Pesquisa:** ao abrir sem texto, mostrar todos os clientes na ordem recebida. Enquanto o
  usuário digita, filtrar por nome exibido ou chave com `casefold()` e ignorar espaços nas
  pontas da consulta. Preservar a ordem original dos resultados; busca sem correspondência
  mostra “Nenhum cliente encontrado”. Digitar e mover o destaque nunca disparam callback.

  **Confirmação e saída:** clique em resultado ou `Enter` sobre resultado destacado confirma
  somente aquela chave; `↑`/`↓` percorrem resultados, `Esc` fecha e restaura o cliente ativo,
  e `Tab`/perda de foco encerram a busca sem confirmar texto livre. Abrir pelo botão ou por
  `↓` mostra a lista. Resultado vazio ou texto que não foi confirmado restaura o rótulo da
  chave ativa; nenhum desses casos recarrega catálogo/jornadas. Após confirmação, o
  controlador valida a chave e prepara os dados antes de efetivar a troca; se a atualização
  falhar, a chave ativa e o texto mostrado continuam sendo os anteriores.

  **Execução e integração:** o seletor bloqueia digitação, abertura e confirmação enquanto
  seu controlador executa; o próprio callback do controlador também recusa trocas nesse
  estado, inclusive eventos atrasados. Na Execução, a confirmação deve atualizar URL,
  catálogo visível e histórico, respeitando a regra existente de que o Pytest só inicia para o
  cliente ativo na configuração local. Na Sentinela, continua limpando seleções e carregando
  jornadas/testes do novo cliente; a opção separada “todos os clientes” não é uma entrada do
  seletor. A mudança visual não altera `configs.local.yaml`. O callback atual da Execução
  recarrega os itens internamente, mas não redesenha o catálogo visível ao trocar de cliente.
  Por decisão do usuário, redesenhar o catálogo visível na S14.4 para que itens do cliente
  anterior não permaneçam na tela.

  **Adoção incremental:** S14.1 usa o componente nas duas páginas com escolha pela lista e
  callbacks por chave; S14.2 acrescenta filtragem dinâmica sem confirmar texto digitado;
  S14.3 conclui teclado, confirmação e restauração; S14.4 verifica bloqueio, dados
  dependentes e listas extensas nas duas páginas. Em cada etapa, texto não confirmado não
  pode mudar o cliente ativo. S14.5 trata apenas o seletor de Velocidade.

  **Luna liberado para a Sprint 14.**

- [x] S14.1 — extraído `ClientPicker`, compartilhado pela Execução e Sentinela. A lista usa
  chaves estáveis nos callbacks, exibe nome e chave, preserva a ordem configurada, rola e
  limita a altura a dez linhas visíveis. Os controladores mantêm a seleção ativa, preparam os
  dados antes de aceitá-la e bloqueiam o seletor durante execução. Widgets reais confirmaram
  a seleção por chave, o uso nas duas páginas e o bloqueio; compilação passou.
- [x] S14.2 — filtra dinamicamente pelo nome ou chave, ignorando caixa e espaços nas pontas,
  preservando a ordem configurada. Exibe estado vazio e ajusta a altura à quantidade filtrada;
  digitar não confirma cliente. Widget Tk real validou nome, chave, trim, estado vazio, ordem,
  ausência de callback ao digitar e callback pela chave somente ao clicar; compilação passou.
- [x] S14.3 — setas percorrem os resultados com destaque visual, Enter confirma o destacado,
  Escape e Tab cancelam sem trocar cliente, e perda de foco fecha a lista sem confirmar.
  Widget Tk real validou Down + Enter pela chave, Escape, Tab e foco em outro controle; a
  compilação passou.
- [x] S14.4 — troca validada nas páginas Tk reais: Execução atualiza cliente/URL, remove do
  catálogo os testes anteriores e redesenha os do cliente novo; Sentinela carrega jornadas e
  testes novos e limpa jornadas/teste/lote anteriores. Ambas bloqueiam e reabilitam o seletor
  ao iniciar/finalizar execução. Lista sintética de 25 clientes confirmou rolagem com máximo
  de 10 linhas, altura dinâmica no filtro e bloqueio da abertura. Compilação passou.
- [x] S14.5 — seletor de Velocidade usa estado `readonly`, mantendo o menu aberto para
  escolha, mas sem edição do campo. Widget Tk real confirmou as três opções (Rápido, Médio,
  Lento), rejeição de Backspace/Delete/Ctrl+A/tecla e seleção de Médio com callback de 750 ms;
  compilação passou.

## Sprint 15 — navegação recolhida das jornadas da Sentinela

Planejada para o fim da fila atual. A lista de jornadas deve abrir compacta para facilitar a
visão dos módulos disponíveis e deixar a expansão sob controle do usuário.

- [x] S15.1 — novas páginas da Sentinela iniciam com todos os grupos recolhidos. Widgets Tk
  reais com árvore sintética confirmaram que só o primeiro nível aparece; expandir um grupo
  exibe seus filhos imediatos e mantém o nível seguinte recolhido.
- [x] S15.2 — recriar a página inicia recolhida e trocar de cliente recolhe todos os grupos;
  redesenhar a mesma árvore preserva a expansão manual. Widgets Tk reais validaram os três
  fluxos e a compilação passou.

## Sprint 16 — estabilidade visual ao redimensionar e restaurar a janela

Planejada para o fim da fila atual. Corrigir ou reduzir o quadro preto transitório que pode
aparecer quando a janela volta da minimização e garantir uma repintura estável durante as
mudanças de tamanho e de estado da janela no Windows.

- [x] **Gate Sol G16 — diagnóstico e correção escolhida.** Capturas da restauração no Windows
  mostraram a janela preta no primeiro quadro; em cerca de 100 ms a geometria e as bordas já
  estavam corretas, mas os canvases da barra lateral, cabeçalhos, campos, botões e catálogo
  ainda permaneciam pretos. Em aproximadamente 500 ms a interface voltava integralmente, sem
  recriação de página, perda de estado ou falha de layout. A causa observada é o atraso de
  repintura dos widgets/Canvas do CustomTkinter após o remapeamento da janela, ampliado pelos
  grandes contêineres com `fg_color="transparent"`; como até cartões com fundo explícito
  aparecem pretos durante a recomposição, trocar somente os fundos não basta. Correção mínima
  definida: usar `COLORS["page"]` no contêiner central e nas raízes das três páginas e agendar,
  após a restauração, uma repintura pública dos widgets existentes, sem recriar páginas nem
  alterar seu estado. Luna liberado para a correção definida da Sprint 16.

- [x] S16.1 — sequência reproduzida na GUI v2 do Windows. Ao restaurar depois de minimizar,
  cerca de 100 ms após o comando, a amostra da janela tinha 65,6% de pontos pretos e a captura
  mostrava grandes áreas sem repintura; entre 250 e 400 ms a tela já estava recomposta. Ao
  redimensionar de maximizada para 1320×820, a captura em 100 ms mostrou artefatos e sobreposição
  temporária; aos 500 ms ainda havia elementos em transição, mas em 1,5 s a captura direta da
  janela estava totalmente recomposta, sem conteúdo cortado. Maximizar não apresentou defeito
  persistente. Conclusão: atraso transitório de repintura, sem falha permanente de layout. A
  janela foi devolvida ao estado maximizado.
- [x] S16.2 — o contêiner central e as raízes das páginas Execução, Sentinela e Configurações
  agora usam `COLORS["page"]` como fundo explícito. Os frames transparentes menores foram
  mantidos porque estão contidos em cartões com superfície definida. Compilação e inspeção
  runtime confirmaram o token efetivo nas quatro superfícies.
- [x] S16.3 — a janela registra os eventos de ocultação e mapeamento e agenda, 50 ms após
  voltar a ficar visível, a repintura dos contêineres compostos existentes. O redesenho usa
  `configure`/`update_idletasks`, cobre frames, abas, listas roláveis e caixas de texto, e não
  recria páginas. Uma validação isolada concluiu o callback preservando a página Execução; na
  restauração real, a amostra de pixels pretos caiu de 31,1% aos ~25 ms para 1,6% por volta de
  75 ms. Compilação e execução do callback passaram.
- [x] S16.4 — validação visual real nos temas Sistema, Claro e Escuro, no tamanho mínimo e
  maximizado. Com Tcl 8.6.15 do Python 3.14 usado pelo `.venv`, `geometry("1024x700")` foi
  confirmado no Tk e a captura externa ficou em 1026×732 com decoração da janela. Após 1,6 s,
  o layout mínimo estava limpo e utilizável nos três temas; maximizado, também recomposto, sem
  sobreposição ou corte persistente. No Windows desta validação, Sistema acompanha o modo escuro.
  Minimizar/restaurar mostrou o primeiro quadro incompleto, mas capturas após 100 ms de espera
  (302–326 ms totais entre ativação e captura) estavam recompostas em Sistema, Claro e Escuro.
  A instância de teste desativou gravação de preferências; nenhum valor persistente foi alterado.
  Sprint 16 concluída.

## Sprint 17 — refinamentos de uso da Sentinela

Planejada para o final da fila. Só iniciar depois que o usuário concluir a validação manual
da pausa e retomada da Sprint 10 e pedir para avançar. Corrigir os pontos de seleção e
configuração identificados no uso real da tela:

- [x] **Gate Sol G17 — contrato de seleção e persistência fechado.**

  **Uma ou duas jornadas:** a execução simples de uma jornada volta a ser o caminho padrão.
  Selecionar uma jornada válida já habilita o início; selecionar outra jornada distinta monta
  opcionalmente o lote paralelo, preservando o teto definitivo de duas execuções. Clicar numa
  jornada selecionada a remove. Com duas selecionadas, uma terceira continua recusada sem
  substituir escolhas silenciosamente. A ordem de seleção define somente a apresentação e a
  ordem de partida; não mistura estados, logs, artefatos ou controles dos dois registros.

  **Destaque da seleção:** cada linha selecionada deve combinar três sinais redundantes:
  preenchimento com a cor selecionada do tema, borda visível e marca textual `✓`. Hover e foco
  de teclado não podem parecer seleção confirmada. O mesmo estado deve sobreviver à recriação da
  página e permanecer legível nos temas Sistema, Claro e Escuro, sem depender da prévia ou do
  resumo abaixo da árvore.

  **TTL:** a preferência sai da Sentinela e passa para a aba Geral de Configurações, sob o nome
  `Retenção dos runs da Sentinela`. O valor inicial continua sendo 7 dias, herdado do
  `ttl_dias` atual quando ainda não existir preferência local. Depois da primeira gravação
  válida, `preferences.local.json` passa a ser a fonte da GUI. Aceitar somente inteiro de 1 a
  365, persistir atomicamente apenas valores válidos e manter o último valor válido se a edição
  for vazia ou inválida. A CLI e `sentinela/config.yaml` conservam seu fallback para uso fora da
  GUI; toda execução iniciada pela GUI recebe explicitamente o TTL persistido, que continua
  governando a limpeza no início do run.

  **Busca de teste específico:** substituir o menu por um seletor pesquisável baseado na
  interação do `ClientPicker`, limitado visualmente a dez resultados com rolagem. A busca é
  sem distinção de caixa ou acentos e casa por nome exibido ou path completo. Ao abrir, o campo
  recebe foco; `↑`/`↓` percorrem ciclicamente os resultados, `Enter` confirma o destacado e
  `Esc`/`Tab` fecham sem alterar a seleção. Clique confirma diretamente. Consulta sem resultado
  mostra `Nenhum teste encontrado`, não habilita início nem apaga uma seleção já confirmada.
  Ao trocar cliente, fechar a pesquisa, limpar as seleções incompatíveis e reconstruir a lista
  somente com o catálogo disponível para o novo cliente; nenhuma troca pode iniciar execução.

  **Fronteira liberada:** implementar somente S17.1–S17.5 dentro de `gui_v2/`, preservando a
  CLI, o teto de duas execuções, o isolamento por ID e as configurações versionadas existentes.
  O gate não altera comportamento por si só.
- [x] S17.1 — tornar a segunda jornada simultânea opcional: uma jornada válida agora habilita
  início e gera um único comando/registro; a segunda continua opcional e, quando selecionada,
  gera o lote paralelo de dois registros isolados. A prévia e o estado de prontidão distinguem
  uma jornada de duas. Mantidos limite de duas e validações existentes.
- [x] S17.2 — jornadas selecionadas agora usam preenchimento do tema, borda acentuada e marca
  `✓` diretamente na linha. Linhas sem seleção mantêm preenchimento neutro e borda discreta;
  foco de teclado recebe contorno próprio, sem imitar o preenchimento e a marca da seleção.
  Como a árvore é redesenhada a partir do conjunto selecionado, o destaque acompanha as
  seleções restauradas e continua vinculado aos tokens de cor aplicados nos temas.
- [x] S17.3 — TTL removido da tela Sentinela e adicionado à aba Geral de Configurações. Valor
  local válido entre 1 e 365 dias é salvo automaticamente em `preferences.local.json` e aplicado
  aos próximos comandos da GUI. Sem preferência, herda `ttl_dias` (7) do YAML; arquivos locais
  antigos continuam válidos. Edição vazia/inválida mostra erro sem substituir o último valor
  salvo. A GUI ainda passa o TTL à limpeza pelo argumento existente; YAML/CLI mantêm fallback.
- [x] S17.4 — lista substituída pelo seletor pesquisável `TestPicker`, com até dez resultados
  visíveis e rolagem. Busca por nome ou path ignora caixa e acentos; foco inicial, setas,
  `Enter`, clique, `Esc` e `Tab` seguem a interação do seletor de clientes. Lista vazia informa
  ausência de resultados e não altera eventual teste já confirmado. Ao trocar cliente, o popup
  fecha, seleção e lote são limpos e a lista recebe apenas o catálogo elegível daquele cliente.
- [x] S17.5 — smoke de widgets Tk reais no `.venv` confirmou uma/duas jornadas e remoção,
  destaque imediato por marca/cor/borda nos quatro acentos, TTL válido e preservação do último
  valor em edição vazia; `PreferencesService` persistiu TTL válido e recusou 366 em diretório
  temporário; `TestPicker` passou lista de 12 itens/rolagem, busca sem caixa/acentos por nome e
  path, setas/Enter, estado vazio preservando seleção confirmada, catálogo vazio e troca de
  cliente sem iniciar execução. O smoke revelou e corrigiu a falta de redesenho da árvore em
  `set_plans()`. Inspeção visual na janela GUI v2 maximizada confirmou seleção/destaque de uma e
  duas jornadas, atualização da prévia, filtro por nome, mensagem `Nenhum teste encontrado` e
  retenção padrão de 7 dias nas Configurações. Com zero testes selecionados, o botão de execução
  parece ativo; inspeção do controlador confirmou aviso e retorno antes de iniciar Pytest. O
  botão foi acionado somente sem seleção: mostrou aviso e não iniciou Pytest. Na validação
  visual mais recente, a troca de Teste específico para Jornada limpou a seleção, mas manteve
  texto antigo na prévia. Corrigido em `SentinelPage._render_mode()` para restaurar a instrução
  inicial do lote ao entrar em Jornada; `py_compile` passou no Python do `.venv`. A janela real
  não pôde ser recapturada após a correção porque a ponte de controle perdeu a conexão; manter
  Após reiniciar a GUI, validação visual confirmou a troca Jornada → Teste específico, a seleção
  de um teste via Enter e o retorno a Jornada com prévia “Prévia do lote · 0/2 jornadas” e texto
  inicial, sem conservar o path específico. Nenhuma execução foi iniciada.

## Correção — popups em múltiplos monitores

- [x] **Gate Sol — posicionamento de popups flutuantes.** O defeito está nos cálculos
  independentes de `ClientPicker.open()` / `_render_results()` e `TestPicker.open()` /
  `_render_results()`: coordenadas root do Tk são globais, mas os limites e clamps atuais
  presumem origem `(0, 0)` e dimensões da tela principal. Isso desloca ou corta popups quando
  a janela está em monitor secundário, inclusive com origem negativa. Alterar os dois seletores
  e adicionar `gui_v2/components/popup_geometry.py` como cálculo compartilhado. No Windows,
  obter área útil do monitor da janela proprietária; posicionar e limitar o popup nessa área,
  preservando abertura acima ou abaixo, largura limitada, reposicionamento após filtrar, foco,
  navegação e seleção. Usar a área virtual do Tk como fallback se a consulta nativa falhar.
  Risco principal: coordenadas multi-monitor/DPI e conversão entre Tk e Win32. Verificar cálculo
  nos quadrantes e origens negativas, compilação e, quando disponível, reprodução manual movendo
  a GUI entre monitores e filtrando os dois popups. Não alterar outros seletores nem a janela
  principal nesta sprint. Luna liberado para este recorte.

- [x] Implementação: os dois popups usam a geometria compartilhada e a área útil do monitor
  proprietário; busca redimensionada recalcula também a posição. py_compile passou e cálculos
  controlados cobriram monitor à direita, origem negativa à esquerda, abertura acima e popup
  maior que o monitor. A reprodução visual com dois monitores permanece pendente.

## Ajuste — sensibilidade do scroll do catálogo de testes

- [x] A rolagem do catálogo da Execução usa incremento vertical de 4 px por unidade no Windows,
  contra 1 px no padrão do CustomTkinter. Com a conversão da roda `delta / 6`, um giro comum
  passa de cerca de 20 px para 80 px (aproximadamente duas linhas de teste). A alteração fica
  restrita ao catálogo; demais listas e plataformas mantêm a rolagem padrão.

