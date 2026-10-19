# ASI Automação — nova GUI

Última atualização: 2026-09-25.

Este arquivo é o mapa de arquitetura e decisões da nova interface. Cada sessão deve começar
por sua leitura completa. O checklist e o status das sprints ficam em [SPRINTS.md](SPRINTS.md).
O código prevalece em caso de divergência; decisões arquiteturais alteradas devem ser
atualizadas aqui.

## 1. Objetivo

Criar uma interface desktop moderna, inspirada no ASI 4.0, sem reescrever as engines
Python. A nova GUI usa CustomTkinter e só substituirá a Tkinter atual depois de atingir
paridade funcional, ser validada e receber aceite explícito. Até lá, ambas coexistem.

Prioridades:

1. Aparência moderna para usuários e apresentações a gestores.
2. Clareza para públicos técnicos e não técnicos.
3. Arquitetura simples de manter, testar e expandir.
4. Paridade segura com Pytest e a futura suíte Genesis da Sentinela.
5. Integração progressiva da Sentinela.

Público estimado: cerca de 50 usuários. Plataforma inicial: Windows. O uso normal inclui
máquinas com dois monitores; simplicidade e baixo consumo importam.

## 2. Método obrigatório

- Trabalhar em **micro-sprints de aproximadamente cinco minutos ou menos**.
- Cada rodada contém apenas uma mudança ou pequeno grupo coeso.
- Informar o recorte antes de editar; verificar e parar para validação ao terminar.
- Não implementar itens futuros por conveniência.
- Se não couber no recorte, dividir antes de começar.
- Não conectar engines sem sprint explicitamente aprovada.
- Não alterar a GUI antiga sem autorização específica.
- **Escopo rígido da nova GUI:** nas sprints de `gui_v2/`, não modificar arquivos sob
  `gui/`, `sentinela/`, `genesis/` ou outras engines. Eles são fontes externas somente de
  leitura; qualquer exceção exige autorização explícita do usuário antes da edição.
- Não fazer commit, `svn add` ou publicação sem solicitação.
- Preservar mudanças locais e reler o arquivo antes de editar.

Ao encerrar uma sessão, informar: micro-sprint concluída, arquivos modificados, validações,
pendências e próxima micro-sprint recomendada, sem iniciá-la automaticamente.

## 3. Decisões confirmadas

### Produto e tecnologia

- Nome: **ASI Automação**.
- CustomTkinter 6.0.0, validado com Python 3.14.2 no Windows.
- CustomTkinter é só a camada visual; engines continuam processos Python separados.
- Não introduzir Electron, servidor web, React ou infraestrutura equivalente.
- Abrir diretamente em **Execução**, maximizada; mínimo `1024×700`.
- Temas Sistema, Claro e Escuro; menu lateral fixo.
- GUI antiga e lançadores permanecem durante a migração.

Menu atual: Execução, Sentinela, Genesis e Configurações. A permanência da página Genesis
como item separado é transitória e será decidida no planejamento da Sentinela. Ícones do menu
são desenhados em memória para não depender de fontes do Windows; item ativo fica vermelho.
Ícones de módulos em `gui/icons/` são reutilizados com variantes para claro/escuro.

### Execução normal

- Cliente, URL somente leitura/copiável e velocidade no topo; não há seletor de ambiente.
- Rápido `0 ms`, Médio `750 ms`, Lento `1500 ms`.
- Busca por nome amigável ignorando caixa e acentos.
- Seleção individual e por seção; sem “selecionar todos” global.
- Mostrar quantidade e resumo na ordem do catálogo.
- Trocar módulo limpa a seleção; trocar cliente também deverá limpar após integração.
- Preservar ordem e `pytest -x` (parada na primeira falha).
- Seleção permanece marcada ao terminar.
- Executar transforma-se em Parar durante execução.
- Fechar durante execução exige confirmação; no protótipo, confirma e interrompe a simulação.
  Encerramento do processo real será integrado junto ao supervisor.
- Sem histórico, favoritos, reexecução ou busca por caminho neste estágio.
- Não criar painel separado de resultados; modernizar logs.

### Módulos

Principais: Almoxarifado, Patrimônio e Corporativo. O quarto card é **Outros módulos**:

- permanece disponível;
- mostra Testes Específicos primeiro;
- mostra somente módulos ativos em `gui/catalog/modules_catalog.py`;
- quando integrado, aplica `gui/core/module_filter.py` ao cliente e versão;
- módulos vazios ou removidos pelo filtro não aparecem;
- nunca duplicar catálogo ou regras na nova GUI.

O ASI também possui Frotas, Imóveis, Registro de Preço, Compras, Penalização, Gestão e
Governança, Orçamentário, Financeiro e Contratos. Só aparecem quando houver testes no
catálogo ativo e restarem itens após o filtro do cliente.

### Logs

- Painel na página Execução; lixeira limpa só a tela.
- Nova execução não limpa automaticamente.
- Preservar autoscroll e suspendê-lo quando o usuário subir.
- Expandir oculta catálogo/resumo e ocupa a área principal; Restaurar recompõe sem perder
  seleção ou conteúdo. Não implementar divisor arrastável agora.
- Futuro: modo simplificado padrão e completo com stacktrace; filtro antes da execução.
- Logs completos permanecem em disco.

### Codegen

- Botão próximo à URL abre `python -m playwright codegen <URL>`.
- Validar HTTP/HTTPS e host; nunca usar `shell=True`.
- Na arquitetura definitiva, subprocesso pertence a serviço próprio.

### Política da URL

- A URL exibida é somente leitura e copiável. A URL explícita em `clientes.<chave>.url` tem
  precedência; durante a migração, `ConfigurationService` aceita a URL única não vazia em
  `ambientes`. Se houver mais de uma URL legada distinta, a configuração é rejeitada para
  evitar escolher um destino implicitamente. Não há seletor de ambiente nem persistência da
  URL em preferências; `configs.yaml` permanece somente leitura.

### Genesis

- Direção confirmada: deixa de ser uma engine/fluxo próprio e passa a ser uma série de testes
  da Sentinela, executada em ordem específica.
- A refatoração do Genesis está em curso fora da GUI; esta interface não a executa nem muda
  flows, blueprint ou configuração enquanto o contrato não estiver definido.
- A forma de apresentar/acionar a suíte e o destino da página Genesis atual exigem pesquisa e
  planejamento com o Sol antes de qualquer integração.

### Sentinela

- Página própria, demonstrativa no protótipo.
- Primeira integração: um cliente e módulo por vez.
- Mostrar plano/quantidade; preservar ordem e duplicatas de `ordem.yaml`.
- Retentativas vêm de `sentinela/config.yaml`, sem editor inicial.
- Preservar HTML; relatório/pasta abrem somente por clique.
- Cancelamento deve preservar relatório parcial quando possível.
- Teste específico, `--count`, multi-cliente e concorrência são sprints posteriores.

### Trilha da Sentinela e migração Genesis

`SENTINELA_SPRINTS.md` é a fonte de verdade do escopo e status da integração da
Sentinela; `SPRINTS.md` mantém o índice geral. A hierarquia e a ordem vêm dos
blocos lógicos de `sentinela/ordem.yaml`, filtrados pelo catálogo e pelas regras
de cliente/versão. O path físico de um teste não define a jornada a que pertence.
O primeiro recorte oferece módulo ou submódulo completo para um cliente; teste
único e opções ampliadas ficam em fase posterior. `tests/genesis` é uma jornada
explícita (`somente_explicito`) e substitui o antigo adaptador Genesis separado.
O cancelamento pode exigir trabalho específico na engine antes do aceite final.

### Preferências

- Preferências da `gui_v2` ficam em `gui_v2/preferences.local.json`, ao lado do código para manter a configuração autocontida no checkout. `svn:ignore` cobre esse arquivo e os temporários `.preferences.local.json.*.tmp` usados na gravação atômica, sem ignorar outras configurações locais.
- O arquivo será JSON UTF-8 com `schema_version` para permitir evolução do formato; arquivo ausente, inválido ou com versão desconhecida usa os padrões da aplicação.
- O escopo inclui tema, velocidade, nível dos logs, saída completa e visibilidade do navegador.
  A velocidade usa `0`, `750` ou `1500` ms, começa em `0` (Rápido) e é enviada ao Pytest em
  `ASI_SLOW_MO`. Não armazenar credenciais, URL, cliente ou ambiente nesse arquivo.
- Cliente ativo continua sob `configs/configs.local.yaml`; preferências não modificam YAML versionado, blueprint ou `ordem.yaml`.
- A gravação é atômica, para não deixar o arquivo parcial se a aplicação for interrompida.

## 4. Estado atual

Arquivos: `gui_v2/main.py` (entrada), `gui_v2/app.py` (shell) e
`gui_v2/controllers/demo_execution_controller.py` (controlador transitório da execução).
`requirements.txt` contém `customtkinter==6.0.0`.

Executar:

```powershell
.\.venv\Scripts\python.exe -m gui_v2.main
```

Já existe:

- janela maximizada, sidebar e quatro páginas;
- tema, velocidade, nível dos logs, saída completa e visibilidade do navegador carregados e
  persistidos localmente; velocidade afeta `ASI_SLOW_MO` no Pytest;
- clientes e URLs carregados da configuração; URL somente leitura/copiável; velocidade ainda demonstrativa;
- Codegen funcional;
- três módulos principais e “Outros módulos”;
- outros módulos baseados nas chaves ativas do catálogo;
- catálogo real, busca, seleção e resumo;
- execução dos testes selecionados na ordem do catálogo via `PytestService` +
  `ProcessSupervisor`, com `-x`; eventos chegam à UI pela fila consumida com `after()`;
- TSE é a referência de validação v3 após instabilidade do PCDF; CJF é a referência v4.
  Consulta de Material passou pelos runners antigo e novo nos dois clientes;
- painel de logs expansível com saída real do processo;
- páginas demonstrativas de Sentinela, Genesis e Configurações.

`App` já se limita à janela, sidebar, contêiner, troca de páginas e injeção do controlador.
O controlador ainda é transitório e poderá ser reduzido nas próximas sprints, sem reintroduzir
widgets no `App`.

Ainda não integrado: Genesis, Sentinela, efeitos das preferências nos motores e histórico.
A execução usa o cliente ativo da configuração; a interface bloqueia quando o cliente
selecionado diverge.

## 5. Diagnóstico arquitetural

`gui_v2/app.py` chegou a cerca de 800 linhas, concentrando janela, páginas, componentes,
assets, estado, catálogo, Codegen e simulação. Isso serviu ao protótipo, mas não é base
adequada para engines. `App` não deve continuar crescendo.

Problemas antes das engines:

1. Catálogo demonstrativo e real coexistem.
2. `catalog_module_names()` usa AST; é transitório.
3. Seleção usa `(módulo, nome)` e pode colidir; deve usar path/nodeid.
4. Estado de domínio e widgets estão misturados.
5. Páginas são reconstruídas sem modelo de estado explícito.
6. Codegen é iniciado pela página.
7. Não há contrato de eventos para processos.
8. Ajuste do dropdown usa `_dropdown_menu`, API privada; deve ficar isolado.

A GUI antiga tem componentes/runners, mas runners recebem `App` e chamam métodos privados.
Reaproveitar conceitos/comandos, não esse acoplamento.

## 6. Arquitetura-alvo

```text
gui_v2/
├── main.py
├── app.py                         # shell e troca de páginas
├── theme.py                       # cores, fontes e dimensões
├── assets.py                      # ícones e imagens
├── models/
│   ├── app_state.py
│   ├── test_item.py
│   └── execution.py
├── pages/
│   ├── execution_page.py
│   ├── sentinel_page.py
│   ├── genesis_page.py
│   └── settings_page.py
├── components/
│   ├── sidebar.py
│   ├── page_header.py
│   ├── client_selector.py
│   ├── module_selector.py
│   ├── test_catalog.py
│   ├── selection_summary.py
│   └── log_panel.py
├── controllers/
│   └── app_controller.py
└── services/
    ├── catalog_service.py
    ├── configuration_service.py
    ├── codegen_service.py
    ├── pytest_service.py
    ├── preferences_service.py
    └── process_supervisor.py
```

### Limites

`App`: cria janela, sidebar e contêiner, troca páginas e injeta dependências. Não conhece
comandos de engines e não lê/grava YAML.

`AppState`: dados sem widgets — página, tema, cliente, URL, velocidade, módulo,
paths/nodeids selecionados, execução e preferências.

`TestItem`: nome, path real, módulo, seção e metadados de apresentação/visibilidade.

Estados: `IDLE`, `STARTING`, `RUNNING`, `STOPPING`, `SUCCEEDED`, `FAILED`, `SKIPPED`,
`INTERRUPTED`.

Páginas: organizam componentes, recebem dados e emitem callbacks. Não abrem processos,
alteram YAML ou importam outras páginas.

Componentes: pequenos, com estado visual local e APIs como `render`, `set_enabled`,
`append`, `clear`. Não conhecem cliente nem processos.

`AppController`: coordena ações, atualiza estado, chama serviços e converte eventos. Não
constrói widgets. Não usar framework de injeção; construção explícita basta.

Serviços: não importam CustomTkinter e são testáveis sem janela.

- `CatalogService`: catálogo real + filtro por cliente, converte para `TestItem`, preserva
  ordem e elimina AST/dados demonstrativos.
- `ConfigurationService`: adapta `ConfigService`, separa leitura/persistência e protege
  preferências pessoais.
- `CodegenService`: valida URL, monta comando e acompanha seu processo.
- `ProcessSupervisor`: inicia um processo controlado, lê stdout/stderr em threads e publica
  eventos em `queue.Queue`; inicia leitores antes do monitor de saída para evitar corrida em
  processos rápidos. Ao final publica `PROCESS_EXITED` com código de retorno. `stop()` encerra
  apenas esse filho e `wait()` aguarda a drenagem dos pipes e o evento final; uma nova execução
  só começa após essa conclusão. A UI consome com `after()`. Nunca chama widgets. Adaptadores
  futuros montarão comandos de engines.
- `PytestService`: adapta paths/nodeids selecionados, na ordem do catálogo, para
  `python -m pytest -x -v -s -p no:randomly`, encaminha stdout/stderr ao vivo, classifica
  sucesso/falha/skip e delega a supervisão ao `ProcessSupervisor`.

## 7. Regras de processos

- Tk só é atualizado na thread principal.
- Threads auxiliares apenas leem processo e enfileiram eventos.
- Cada execução tem identidade, PID, engine, horário, estado e diretórios.
- Parar entra em `STOPPING`; não liberar antes de o processo sair.
- Fechar confirma e encerra apenas filhos próprios.
- Nunca matar todos os Python/Chromium da máquina.
- Sentinela tenta cancelamento cooperativo; `taskkill /F /T` é fallback.
- Antes de paralelismo, isolar configuração, logs, evidências, traces e relatórios.

## 8. Regras de catálogo/configuração

- Fonte única: `gui/catalog/modules_catalog.py`.
- Disponibilidade: `gui/core/module_filter.py`.
- Preservar ordem; nunca duplicar testes.
- Eliminar AST na versão funcional.
- Cliente exibido mapeia para chave real; versão alimenta filtro v3/v4.
- Troca de cliente limpa seleção e recalcula catálogo.
- URL direta do cliente prevalece; temporariamente, uma única URL legada não vazia sob
  `ambientes` é aceita. Campo somente leitura/copiável e sem seletor de ambiente.

## 9. Regras de logs

- Eventos internos: tipo, nível, mensagem e timestamp.
- Preservar stdout não estruturado do Pytest.
- Console e TXT diferem; modo simples afeta apenas apresentação.
- Tracebacks multilinha exigem blocos/eventos, não filtro ingênuo por linha.
- `LogPanel` só apresenta; não conhece subprocessos.

## 10. Sprints e micro-sprints

O plano detalhado, o status e a próxima micro-sprint ficam em [SPRINTS.md](SPRINTS.md).
Cada checkbox representa uma alteração pequena que deve ser validada antes da próxima.

## 11. Riscos conhecidos

- `taskkill /F /T` pode impedir relatório/restauração da Sentinela; usar como fallback.
- Concorrência pode colidir configuração e artefatos mesmo no mesmo cliente.
- `--count`, retry da Sentinela e retry de login são mecanismos diferentes; credencial
  definitivamente recusada nunca deve ser retentada até bloqueio.
- Logs/tracebacks multilinha impedem filtragem textual ingênua.
- CustomTkinter pode mostrar artefatos mínimos de antialiasing com escala do Windows;
  não criar máscaras frágeis para escondê-los.

## 12. Qualidade

- Sem regressão na GUI antiga.
- Sem segredos em código, logs ou screenshots.
- Sem preferências pessoais versionadas.
- Sem UI fora da thread principal ou processos órfãos.
- Sem duplicação de catálogo; identidade por path/nodeid.
- Serviços testáveis sem janela; mudanças pequenas e revisáveis.
- Type hints/docstrings quando definirem contrato; verificação proporcional ao risco.

## 13. Próxima micro-sprint

Consultar [SPRINTS.md](SPRINTS.md), que mantém o status e resume o próximo escopo.
