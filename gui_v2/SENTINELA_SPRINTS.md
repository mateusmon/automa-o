# Sentinela na GUI v2 — trilha de integração

Este arquivo é a fonte de verdade do escopo e do status das microsprints da Sentinela
na GUI v2. `SPRINTS.md` mantém somente o índice das sprints gerais. Os contratos da
engine continuam no código de `sentinela/`; esta trilha não autoriza alterá-la.

## Contrato verificado no código em 2026-09-25

- `sentinela/ordem.yaml` define jornadas lógicas por `modulo`, em ordem. Um bloco pode
  incluir pré-condições cujo path físico pertence a outra pasta. Repetições são
  intencionais. `somente_explicito: true` exclui o bloco da execução global, mas
  permite sua seleção explícita. `tests/genesis` já usa essa marcação.
- `sentinela/ordem_reader.py` seleciona um prefixo de módulo com seus descendentes;
  preserva a ordem, as duplicatas e a posição global de cada ocorrência.
- `sentinela/catalog_reader.py` aplica o catálogo e o filtro de cliente/versão.
  A GUI deve usar essas fontes, sem inventar a hierarquia a partir das pastas de testes.
- CLI atual: `python sentinela/sentinela.py --cliente CHAVE --modulo PREFIXO`, com
  `--dry-run` para inspeção. `--teste` ignora `ordem.yaml` e fica para a trilha ampliada.
- `runner.py` gera relatório HTML no `finally` se houver resultados. `executor.py`
  executa cada teste em subprocesso; o cancelamento da árvore de processos requer
  cuidado além do `ProcessSupervisor.stop()` usado pelo Pytest simples.

## Escolhas de produto para a integração

- Fonte dos identificadores e da hierarquia: `ordem.yaml`. Nomes amigáveis podem vir
  do catálogo quando houver correspondência; o identificador lógico continua visível.
- Seleção inicial: um cliente e um prefixo lógico de `--modulo` por execução. O prefixo
  pode representar módulo completo (`tests/almoxarifado`) ou submódulo
  (`tests/almoxarifado/movimentacao_interna`). Um teste único fica na fase ampliada.
- Mostrar `tests/genesis` como opção explícita da Sentinela. A página Genesis separada
  só será removida após a migração e o aceite previstos na microsprint final.
- O plano exibe a lista filtrada para o cliente, com cada ocorrência e sua ordem.
  A quantidade conta ocorrências, não paths únicos. Caminhos inválidos devem ser
  sinalizados antes de oferecer execução.
- A integração inicial usa as tentativas e o TTL da configuração existente da
  Sentinela. Relatório e pasta são abertos somente por ação do usuário.

## Sprint 7 — integração essencial

Cada item é uma microsprint independente, com revisão antes da seguinte. Alterações
ficam em `gui_v2/`; `gui/`, `sentinela/`, `genesis/` e engines são somente leitura.

- [x] **S7.1 — modelo de jornadas.** Serviço sem widgets lê os blocos lógicos de
  `ordem.yaml` e aplica o filtro canônico de cliente/versão. Inclui apenas prefixos
  com ocorrências disponíveis; preserva os blocos explícitos. Concluído quando
  clientes v3 e v4 retornam opções filtradas, incluindo Genesis explícito.
- [x] **S7.2 — seleção na página.** Substituir os três cards fixos por jornadas
  derivadas do serviço, com seleção de módulo/submódulo e cliente real. Troca de
  cliente limpa seleção e recalcula as opções. Concluído quando a página não
  apresenta contagens demonstrativas nem jornadas indisponíveis. Módulos com
  submódulos podem expandir/recolher; o hover mantém contraste na jornada selecionada.
- [x] **S7.3 — plano local.** Produzir a lista ordenada das ocorrências do prefixo
  selecionado, após o filtro do cliente, mantendo pré-condições externas e
  duplicatas. Exibir quantidade e avisos de paths inválidos. Concluído quando
  o plano visível corresponde à seleção da CLI para o mesmo cliente/prefixo.
  Confirmado com CJF v4: 187 ocorrências na mesma sequência da CLI.
- [x] **S7.4 — inspeção sem executar.** Mostrar o plano e a contagem na UI antes
  do início; conferir com `--dry-run` em recortes v3/v4. Bloquear início com plano
  vazio ou path inválido. Nenhum navegador deve abrir nessa etapa. Concluída:
  prévia marcada como conferida ou bloqueada, sem ação de execução; TSE v3 e
  CJF v4 coincidem com a CLI em 63 ocorrências cada, na mesma ordem.
- [x] **S7.5 — adaptador de comando.** Montar apenas `--cliente` e `--modulo` para
  a CLI existente, com diretório de trabalho e Python do ambiente atual.
  Encaminhar opções de execução somente quando seu contrato estiver integrado.
  Concluída quando o comando construído reproduz o plano exibido. Validado com
  TSE v3 e CJF v4: 63 ocorrências na mesma sequência; o adaptador não inicia processos.
- [x] **S7.6 — execução supervisionada.** Conectar Iniciar/Parar para um cliente
  e um prefixo lógico, impedindo execução concorrente. Preservar tentativas/TTL
  da Sentinela e apresentar saída em painel próprio. Concluído após uma execução
  curta em ambiente autorizado, com estado final e seleção coerentes. Concluída:
  controles e saída integrados ao supervisor; jornada CRUD de Característica do
  Bem no TRE-PE v3 passou nos quatro casos, e `configs.local.yaml` permaneceu em
  `trepe`.
- [x] **S7.7 — relatório e pasta.** Associar à execução o diretório criado pela
  Sentinela e habilitar ações de abrir relatório HTML e pasta apenas quando os
  caminhos existirem. Concluída: caminhos informados na saída da CLI são
  validados dentro de `sentinela/reports`; links de execuções anteriores são
  limpos ao trocar cliente ou jornada. Conferidos os artefatos reais do TRE-PE,
  com abertura do HTML no navegador e da pasta no Explorer; caminhos ausentes e
  externos permanecem indisponíveis.
- [x] **S7.8 — cancelamento e restauração.** Definir e verificar encerramento da
  árvore supervisionada sem afetar processos externos, aguardar a saída, mostrar
  relatório parcial quando gerado e conferir a restauração de
  `configs/configs.local.yaml`. Concluído após cancelamento durante um teste em
  ambiente autorizado: o supervisor envia Ctrl+Break e aguarda encerramento
  gracioso, usando Job Object no Windows para encerrar descendentes se necessário;
  a execução no TRE-PE encerrou sem processo órfão, e o hash da configuração local
  permaneceu igual com `trepe` ativo. O teste interrompido não gerou relatório
  parcial, portanto os controles de relatório/pasta permaneceram indisponíveis;
  quando a CLI reporta artefatos, a GUI valida os caminhos e os apresenta.

## Dependências e fases seguintes

- Antes de S7.6, escolher um cenário curto autorizado. Um dry-run não valida o
  comportamento de execução, relatório ou cancelamento.
- S7.8 pode exigir mudança na engine para cancelamento cooperativo e relatório
  parcial. Isso deve ser planejado como tarefa separada, fora do escopo rígido da
  `gui_v2`, antes da edição de `sentinela/`.
- A trilha ampliada posterior cobre `--teste`, `--count`, seleção de todos os
  clientes, TTL editável e trace. Concorrência e pausa permanecem na Sprint 10.
- A antiga Sprint 6 não fornece um adaptador Genesis separado; sua migração usa
  `tests/genesis` como jornada explícita da Sentinela. A aposentadoria da página
  Genesis continua condicionada à validação e ao aceite.

Histórico e status recente das sprints gerais: consulte [SPRINTS.md](SPRINTS.md).

## Sprint 20 — histórico local de runs da Sentinela

- [x] **S20.1 — restaurar os 10 runs mais recentes.** Na inicialização, `SentinelArtifactService`
  valida ID UUID, sufixo do diretório e `.execution-id`, e descobre no máximo dez runs recentes,
  incluindo os que não geraram relatório. O seletor da Sentinela reúne esses itens sob o estado
  `Histórico`, depois das execuções supervisionadas da sessão. Run sem relatório recebe estado
  `SEM RELATÓRIO`, sem inferir que foi interrompido. A ordenação usa a data de início no nome
  da pasta, com modificação como desempate. A lista visível tem limite total de dez itens,
  contando execuções da sessão; processos ativos e resultados recentes da sessão ocupam as vagas
  antes do histórico em disco. Histórico não entra no registro
  de processos e não habilita Pausar/Parar; relatório, pasta e traces são habilitados conforme
  os artefatos encontrados. O filtro de idade usa o mesmo TTL efetivo que a próxima execução
  passaria à engine. O log histórico apresenta ID, horário, pasta e título do relatório quando
  disponível; estado sem falhas só aparece quando os indicadores do HTML puderam ser lidos.
  Alterar o TTL nas Configurações atualiza imediatamente a lista e mantém a seleção se ela ainda
  estiver dentro do prazo.
  O serviço lê relatório apenas dos dez candidatos mais recentes e a saída resumida fica em cache
  durante a sessão. A raiz `sentinela/reports` precisa resolver para dentro da raiz do projeto.

  Validação fora do sandbox: compilação sintática; descoberta dos dez diretórios reais, incluindo
  o run sem relatório; smoke com widgets Tk reais para seleção histórica e controles desabilitados.
  Nenhuma jornada ASI foi iniciada.

- [x] **S20.2 — aumentar o histórico para 20 runs e rolar após sete linhas.** O seletor usa
  `PickerResults` e mantém até 20 opções totais, incluindo execuções da sessão. Runs sem relatório
  seguem selecionáveis quando a pasta existe e está dentro do TTL efetivo. A limpeza automática
  no início de uma nova execução apaga pastas expiradas inteiras, portanto runs removidos deixam
  de ter dados para listar.
