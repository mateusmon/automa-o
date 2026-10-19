# ASI Automação — plano de sprints da GUI v2

Este é o checklist de execução e a fonte de status das sprints da `gui_v2`. Os requisitos,
decisões e limites arquiteturais ficam em [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md). Cada
checkbox corresponde a uma micro-sprint; concluir e validar uma antes de iniciar a próxima.

## Princípios de trabalho

Priorizar eficácia, eficiência, simplicidade e objetividade em todo o projeto. Entregar o
mínimo de estrutura que cumpra o objetivo com clareza, sem abstrações, validações ou opções
prematuras. Antes de cada microsprint, apresentar o recorte para orientação; depois, concluir,
verificar de forma proporcional e parar para revisão antes da próxima.

## Política de modelos — Sol planeja, Luna executa

O objetivo desta marcação é economizar uso sem entregar decisões arquiteturais ainda vagas
ao Luna Light.

- Uma linha `Gate Sol` desmarcada é uma trava obrigatória. Se o modelo atual for Luna,
  **não iniciar a implementação**: avisar ao usuário que é necessário mudar para o Sol Light
  e indicar o identificador do gate pendente.
- O Sol deve inspecionar o código atual e detalhar no próprio gate ou nos itens da sprint:
  arquivos afetados, contrato da mudança, riscos, invariantes e verificação esperada. Depois,
  marca o gate como concluído (`[x]`) e registra “Luna liberado”.
- Com o gate concluído, o Luna executa uma microsprint por vez e para para revisão. Itens sem
  `Gate Sol` podem ser executados diretamente pelo Luna.
- Um gate concluído não libera mudanças além da sprint indicada. Se surgir uma decisão nova
  de arquitetura, concorrência, processo ou persistência, o Luna deve pedir nova passagem
  pelo Sol antes de continuar.

## Sprint 0 — requisitos e protótipo visual

Estado: **protótipo concluído; refinamento visual contínuo**.

- [x] Requisitos e referências visuais.
- [x] CustomTkinter, janela, sidebar e páginas.
- [x] Temas e ícones.
- [x] Busca/seleção demonstrativas e Codegen.
- [x] Logs expansíveis.
- [x] “Outros módulos” pelas chaves ativas do catálogo.
- [x] Aprovação visual final.

## Sprint 1 — fundação arquitetural sem mudar o visual

- [x] S1.1 — extrair `theme.py`: cores, fontes e dimensões.
- [x] S1.2 — extrair `assets.py`: carga/desenho de ícones.
- [x] S1.3 — extrair `Sidebar`.
- [x] S1.4 — extrair `PageHeader`.
- [x] S1.5 — extrair `LogPanel` preservando limpar/expandir/restaurar.
- [x] S1.6 — extrair `ClientSelector` demonstrativo.
- [x] S1.7 — extrair `ModuleSelector` e “Outros módulos”.
- [x] S1.8 — extrair `TestCatalog` e `SelectionSummary`.
- [x] S1.9 — extrair as quatro páginas.
- [x] S1.10 — reduzir `App` a composição/navegação.

Saída: aparência idêntica; `App` sem construção detalhada; componentes isoláveis;
compilação e abertura verificadas após cada extração.

## Sprint 2 — estado e catálogo reais

- [x] S2.1 — `TestItem` por path/nodeid.
- [x] S2.2 — `AppState` sem widgets.
- [x] S2.3 — controlador mínimo de cliente/módulo/seleção.
- [~] S2.4 — não executar: a GUI legada permanece inalterada; o serviço da nova GUI adapta a
  leitura do catálogo sem modificar seu contrato de importação.
- [x] S2.5 — `CatalogService` com catálogo real.
- [x] S2.6 — filtro por cliente/versão.
- [x] S2.7 — remover `MODULES` demonstrativo e AST.
- [x] S2.8 — carregar clientes e configurações reais somente para leitura (antes do recorte URL-only).
- [x] S2.9 — validar troca, limpeza e ordem em clientes v3/v4.

## Sprint 3 — serviços locais e preferências

- [x] S3.1 — extrair `CodegenService`.
- [x] S3.2 — definir `gui_v2/preferences.local.json` ignorado pelo SVN, com JSON versionado.
- [x] S3.3 — persistir e restaurar o tema usando o arquivo local.
- [x] S3.4 — URL somente leitura/copiável; removido seletor de ambiente e priorizada URL do cliente.
- [x] S3.5 — persistir nível de log, saída completa e visibilidade do navegador, sem engines.

S3.3 carrega o tema antes da criação da janela, grava mudanças com substituição atômica e
mantém a seleção do tema coerente ao navegar entre páginas. Se a gravação falhar, o tema
continua aplicado e a interface informa que não foi possível persistir a preferência.

S3.4 removeu o seletor de ambiente: URL direta em `clientes.<chave>.url` tem precedência; na
configuração legada atual, é aceita somente quando há uma única URL não vazia distinta em
`ambientes`. A URL é somente leitura, mas pode ser selecionada e copiada. S3.5 grava também
nível de log, saída completa e visibilidade do navegador no arquivo local ignorado pelo SVN;
essas preferências ainda não alteram a execução dos motores.

## Sprint 4 — infraestrutura de processos com engine falsa

- [x] S4.1 — `ExecutionState` e eventos.
- [x] S4.2 — serviço mínimo para iniciar processo controlado e entregar saída/encerramento
  por fila, sem integrar engines.
- [x] S4.3 — processo simulado com stdout/sucesso.
- [x] S4.4 — simular falha/código de retorno.
- [x] S4.5 — parar e aguardar encerramento real.
- [x] S4.6 — confirmar fechamento em execução.
- [x] S4.7 — impedir eventos tardios na execução seguinte.

## Sprint 5 — Pytest essencial

- [x] S5.1 — um teste selecionado.
- [x] S5.2 — `ASI_SLOW_MO`.
- [x] S5.3 — stdout real.
- [x] S5.4 — sucesso, falha e skip.
- [x] S5.5 — múltiplos paths, ordem do catálogo e parada na primeira falha (`-x`).
- [x] S5.6 — parar/fechar seguro; interromper somente o Pytest supervisionado e aguardar a saída.
- [x] S5.7 — comparar GUI antiga/nova em TSE (v3); Consulta de Material passou nas duas.
- [x] S5.8 — comparar GUI antiga/nova em CJF (v4); Consulta de Material passou nas duas.

Não rodar testes mutantes sem ambiente/cenário aprovado.

## Sprint 6 — Genesis (suspensa; será absorvida pela Sentinela)

- [ ] S6.1 — adaptador do comando.
- [ ] S6.2 — confirmação.
- [ ] S6.3 — velocidade.
- [ ] S6.4 — logs.
- [ ] S6.5 — parada sem afetar processos externos.
- [ ] S6.6 — validar em ambiente autorizado.

## Sprint 7 — Sentinela essencial

Trilha replanejada em [SENTINELA_SPRINTS.md](SENTINELA_SPRINTS.md), fonte de verdade
do escopo e status de cada microsprint da Sentinela. **S7.1 a S7.8 concluídas.** A sequência
é: modelo de jornadas, seleção, plano local, inspeção visual, adaptador do comando,
execução, relatório/pasta e cancelamento/restauração.

## Sprint 8 — apresentação e preferências

- [x] **Gate Sol G8 — contratos definidos para S8.1 a S8.4.**

  **Contrato mínimo:**

  - `ProcessSupervisor` continua responsável apenas por publicar stdout, stderr e encerramento;
    não interpreta Pytest nem conhece apresentação.
  - `PytestService` passa a converter a saída em eventos de execução estruturados. Cada evento
    informa tipo, nível, mensagem e timestamp; eventos de teste informam também o alvo quando
    disponível. Blocos multilinha, especialmente tracebacks, permanecem inteiros.
  - O controlador mantém o estado derivado da execução e decide quais eventos chegam ao painel.
    A página e o `LogPanel` somente exibem dados prontos, sem analisar texto do processo.
  - Saída simplificada mostra início, teste atual, resultado por teste, avisos/erros e resultado
    final. Saída completa mostra também o stdout/stderr original, sem alterar os arquivos de log
    produzidos pela execução.
  - O nível configurado é capturado no início da execução e filtra os eventos apresentados pelo
    controlador. Uma mudança de preferência afeta somente a próxima execução.
  - Progresso usa a quantidade de alvos selecionados e resultados de testes reconhecidos;
    teste atual vem do evento de início do teste; duração usa relógio monotônico entre início e
    encerramento. Se a saída não permitir reconhecer um dado, a interface o deixa indisponível
    em vez de estimá-lo.

  **Arquivos previstos:** `models/execution.py`, `services/pytest_service.py`,
  `controllers/demo_execution_controller.py`, `pages/execution_page.py` e, somente quando a
  apresentação exigir, `components/log_panel.py`. `ProcessSupervisor` não deve mudar sem uma
  necessidade demonstrada durante a implementação.

  **Invariantes:** preservar saída completa, ordem dos eventos, stacktraces multilinha,
  autoscroll, conteúdo ao expandir/restaurar e isolamento entre execuções. Não interpretar logs
  na camada visual nem alterar Pytest, GUI antiga ou engines.

  **Verificação:** usar eventos representativos de sucesso, falha, skip e traceback; conferir os
  dois modos de saída, o filtro capturado antes da execução e progresso/duração sem depender de
  widgets.

  **Luna liberado para S8.1–S8.4.**

- [x] S8.1 — logs simplificados. `PytestService` adapta a saída detalhada para eventos de
  início, resultado por nodeid, resumo e avisos/erros; o controlador mostra somente esses
  eventos no painel simplificado. O teste atual fica indisponível porque `-v` só publica o
  nodeid depois que o resultado é conhecido. Mensagens originais relevantes de falha são
  preservadas por linha. Traceback e exibição completa ficam para S8.2.
- [x] S8.2 — logs completos. O painel alterna entre saída simplificada e saída original;
  a preferência “Saída completa” define o modo inicial e o botão do painel a atualiza.
  `PytestService` preserva stdout/stderr, inclusive linhas vazias de traceback, com publicação
  contínua e uma janela curta para ordenar eventos entre os pipes. O controlador preserva e
  reapresenta o histórico ao alternar modos ou voltar à página; nova execução e Limpar isolam
  o conteúdo. O painel usa o mesmo buffer ao expandir/restaurar. A ordem entre os pipes é
  aproximada pela timestamp dentro da janela; Pytest não fornece sequência global entre stdout
  e stderr independentes.
- [x] S8.3 — filtro de nível antes da execução. O controlador captura a preferência ao iniciar
  e filtra eventos estruturados e saída original pela severidade; linhas `E ...`/`> ...` de
  traceback e cabeçalhos de falha são erro, warnings de Pytest são aviso. Alterações durante a
  execução só valem para a próxima. A classificação de resumo segue falha/erro, skip ou sucesso.
- [x] S8.4 — progresso, teste atual e duração confiáveis. A coleta do Pytest define o total
  real de items; resultados reconhecidos contam o progresso. A saída `-v` informa o alvo junto
  do resultado, não no início, então teste atual fica indisponível em vez de ser inferido.
  Duração usa `monotonic()` no evento de coleta e no encerramento, com atualização durante a
  execução. Sem coleta reconhecida, o progresso fica indisponível; falha parcial mantém a
  contagem real concluída. Coleta real validada com `.venv`/Pytest 9.0.2.
- [x] S8.5 — headless. A preferência capturada no início é passada ao `PytestService`; navegador
  oculto acrescenta `--headless`, aproveitando a fixture existente de `conftest.py`, incluindo
  Chromium sem janela e supressão de pausa interativa em falha. Navegador visível mantém o
  comportamento padrão.
- [x] S8.6 — notificação final. O resumo da execução mostra sucesso, skip, falha ou interrupção
  sem modal; o último resultado permanece visível ao voltar à página e é limpo ao iniciar outra.
  Se o usuário estiver em outra página quando termina, o resumo aparece ao voltar à Execução.

## Sprint 9 — Sentinela ampliada (detalhar após a Sprint 7)

- [x] **Gate Sol G9 — contratos da Sprint 9 definidos após auditoria da CLI e da GUI.**

  **Contrato de seleção e comando:**

  - A Sentinela passa a ter dois modos explícitos e mutuamente exclusivos: `Jornada` mantém o
    fluxo atual (`--cliente CHAVE --modulo PREFIXO`); `Teste específico` escolhe exatamente um
    arquivo disponível no catálogo para o cliente e usa `--cliente CHAVE --teste PATH`.
  - O teste específico vem do catálogo já filtrado por cliente/versão. Texto livre, nodeid,
    diretório, glob e path externo não são aceitos. O serviço valida novamente arquivo,
    extensão `.py`, raiz `tests/` e disponibilidade antes de montar o comando.
  - Trocar modo ou cliente limpa teste, `count`, prévia multi-cliente e artefatos da execução
    anterior. Os controles de seleção permanecem bloqueados enquanto houver processo ativo.
  - `--teste` ignora `ordem.yaml` e não executa pré-condições da jornada. A interface deve
    avisar isso na prévia, sem sugerir que um teste isolado equivale à jornada completa.

  **Contrato de repetição e retentativas:**

  - `count` pertence somente ao modo `Teste específico`, aceita os valores fechados 1, 2 ou 3
    e gera `--count N`; ao voltar para Jornada, retorna a 1 e não envia a flag.
  - `--count` repete o teste inteiro. Cada repetição ainda pode consumir até `tentativas` da
    Sentinela (`sentinela/config.yaml`, atualmente 3), portanto o limite visível é de até
    `count × tentativas` processos Pytest. A prévia mostra essa distinção antes de iniciar.
  - As retentativas internas de `login_flow.py` são um terceiro mecanismo, restrito a falhas
    transitórias de carregamento. Recusas definitivas de credencial interrompem o login e não
    devem ser contornadas, configuradas nem multiplicadas pela GUI. A Sprint 9 não expõe
    `--tentativas` nem altera login, Sentinela ou configuração da engine.

  **Contrato multi-cliente e trava de segurança:**

  - O modo multi-cliente existe somente para **um teste específico por vez**, sequencialmente,
    usando `--todos --teste PATH`. Antes da execução, a GUI mostra a lista e a quantidade de
    clientes nos quais o catálogo disponibiliza o teste; incompatíveis serão ignorados pela
    CLI. `count` continua limitado a 1–3 e o custo total previsto fica visível.
  - A execução exige confirmação explícita contendo teste, número de clientes elegíveis,
    `count` e limite de processos Pytest. Cancelar a confirmação não inicia processo nem altera
    seleção.
  - `SentinelCommandService` deve representar o modo por dados tipados, não por combinações
    livres de flags. É proibido construir `--todos` sem `--teste`; também são inválidos
    `--todos --modulo`, seleção vazia, mais de um teste, diretório e jornada global. A página
    não é a única barreira: o serviço rejeita essas combinações antes do subprocesso.

  **Contrato de TTL e traces:**

  - TTL é uma opção local da execução, não uma preferência persistida. Começa com o valor de
    `sentinela/config.yaml`, aceita inteiro de 1 a 365 dias e é capturado ao iniciar como
    `--ttl N`; não grava YAML nem `preferences.local.json`.
  - A interface informa que o TTL limpa, no início da execução, somente diretórios antigos de
    `sentinela/reports`; não oferece `--limpar` e não promete recuperar runs já removidos.
  - Após o encerramento, o serviço de artefatos pode listar os `*_trace.zip` existentes apenas
    dentro do diretório de run validado. Abrir trace é ação manual por arquivo e lança
    `sys.executable -m playwright show-trace <ZIP>` sem `shell=True`; nunca abre
    automaticamente e nunca aceita caminho fora de `sentinela/reports`.

  **Limites arquiteturais:** mudanças restritas a `gui_v2/`; `sentinela/`, `gui/`, `genesis/`,
  login e configurações são somente leitura. `SentinelController` coordena o estado;
  `SentinelCommandService` valida e monta comandos; `SentinelArtifactService` valida run/trace;
  a página apenas apresenta dados e emite callbacks. A supervisão, o cancelamento seguro e a
  restauração já validados na Sprint 7 devem permanecer intactos.

  **Arquivos previstos:** `services/sentinel_command_service.py`,
  `services/sentinel_plan_service.py`, `services/sentinel_artifact_service.py`,
  `controllers/sentinel_controller.py` e `pages/sentinel_page.py`. Criar um modelo/serviço
  pequeno separado somente se ele eliminar combinações inválidas no domínio; não ampliar
  `ProcessSupervisor` nem alterar engines sem necessidade demonstrada.

  **Verificação obrigatória:** testar a montagem de comandos sem abrir navegador para os dois
  modos, `count` 1–3, TTL nos limites, teste indisponível e todas as combinações globais
  proibidas; conferir que nenhuma delas produz `--todos` sem `--teste`. Comparar uma prévia
  específica com o filtro do catálogo. A validação real começa com um teste curto autorizado
  em um cliente; multi-cliente só depois da confirmação do usuário e com o mesmo teste curto.
  Conferir ao final cancelamento, relatório/pasta, trace sob a raiz permitida e ausência de
  alteração em `configs.local.yaml`.

  **Luna liberado para a Sprint 9, uma microsprint por vez, começando por S9.1.**

- [x] S9.1 — modo Teste específico para um cliente. A página alterna entre Jornada e Teste
  específico, oferece arquivos do catálogo filtrados por cliente/versão, exige escolha explícita,
  avisa que pré-condições não serão executadas e monta somente `--cliente CHAVE --teste PATH`.
  O serviço rejeita itens fora do catálogo e paths fora de `tests/`; montagem aceita/rejeições e
  compilação dos módulos alterados verificadas sem iniciar subprocesso.
- [x] S9.2 — `--count` 1–3. O seletor fechado aparece no modo específico, começa em 1 e exibe
  o limite `count × tentativas` lido de `sentinela/config.yaml`; modo Jornada e troca de cliente
  restauram 1, e Jornada nunca envia `--count`. Comandos 1–3, rejeições fora do intervalo,
  limite de tentativas e compilação dos módulos alterados verificados sem subprocesso.
- [x] S9.3 — um teste específico em todos os clientes. A opção multi-cliente aparece somente
  no modo específico; a prévia lista os clientes elegíveis pelo catálogo, apresenta o custo
  máximo e pede confirmação com teste, clientes, `count` e limite de processos. O comando é
  somente `--todos --teste PATH`, com `--count` quando maior que 1. Montagem/rejeições e
  comparação com o catálogo real (22 clientes elegíveis; máximo de 132 processos para
  `count=2`, 3 tentativas) verificadas sem executar teste real.
- [x] S9.4 — defesa em profundidade contra suíte global. `SentinelCommandService` recebe
  pedidos tipados por modo e centraliza a validação: execução global exige exatamente um teste,
  clientes elegíveis e não aceita cliente/módulo; jornada e teste de cliente único rejeitam
  campos de outros modos. O alvo precisa estar no catálogo, ser arquivo `.py` existente sob
  `tests/` e permanecer dentro da raiz mesmo após resolver symlinks. Oito combinações inválidas,
  os três modos válidos e a compilação foram verificados sem subprocesso.
- [x] S9.5 — TTL local por execução. O campo parte de `ttl_dias` em `sentinela/config.yaml`,
  aceita somente inteiro de 1 a 365 para a execução atual e explica que, ao iniciar, a Sentinela
  remove apenas diretórios antigos dentro de `sentinela/reports`. `--ttl N` é enviado nos três
  modos; não há ação `--limpar` nem persistência. Limites, comandos e hash da configuração
  verificados; os módulos alterados compilaram sem executar a Sentinela.
- [x] S9.6 — abertura manual de traces. A última execução validada lista `*_trace.zip` do seu
  diretório de run, incluindo tentativas, e a página exige escolha e clique em Abrir trace.
  O serviço revalida run/arquivo sob `sentinela/reports`, extensão, existência e symlinks, então
  chama `sys.executable -m playwright show-trace <ZIP>` sem shell. Seleções de cliente, jornada,
  modo ou teste limpam artefatos anteriores. Enumeração, escapes, symlink e comando com abertura
  simulada verificados; módulos alterados compilaram sem iniciar o visualizador.

