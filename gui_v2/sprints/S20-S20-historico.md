# Sprint 20 — histórico local de runs da Sentinela

- [x] **S20.1 — restaurar os 10 runs mais recentes.** A GUI descobre os diretórios locais
  com UUID, sufixo e `.execution-id` coerentes, preservando runs sem relatório. A lista visível
  tem no máximo dez itens somando os registros da sessão atual e o histórico em disco; processos
  ativos e execuções recentes da sessão têm prioridade. A lista os
  identifica como `Histórico`; não os registra como processos ativos nem habilita Pausar/Parar.
  Run sem relatório recebe `SEM RELATÓRIO`, sem inferir o motivo. Relatório, pasta e traces
  dependem dos arquivos validados. A idade segue o TTL efetivo da Sentinela, com ordenação pela
  data de início da pasta; alterar o TTL atualiza a lista. A raiz de relatórios deve resolver para
  dentro do projeto. Os dados de apresentação são resumidos uma vez na inicialização e ficam em
  cache até o TTL mudar.

  **Validação:** compilação sintática e descoberta somente de leitura dos dez runs reais,
  incluindo o run sem relatório; smoke com widgets Tk reais confirmou estado histórico e
  controles de processo desabilitados. Nenhuma jornada ASI foi iniciada.

- [x] **S20.2 — exibir até 20 execuções com viewport de sete linhas.** O limite considera
  o total do seletor, incluindo execuções da sessão; as ativas e recentes da sessão mantêm
  prioridade sobre o histórico em disco. O seletor de execução usa `PickerResults`, com no máximo
  sete linhas visíveis e rolagem/navegação por teclado para opções adicionais. Os demais usos de
  `ClientPicker` preservam seu padrão de dez linhas. Runs com pasta válida e sem `report.html`
  continuam no histórico como `SEM RELATÓRIO`. A listagem respeita o TTL efetivo; se a limpeza
  automática no início de uma nova execução já removeu a pasta expirada, o run não tem mais dados
  locais para ser listado.

  **Validação:** compilação sintática; smoke Tk real com 7, 8 e 20 opções confirmou que sete
  linhas cabem, excedentes rolam, e a navegação por teclado revela e seleciona linhas posteriores.
  Descoberta em diretórios temporários confirmou limite de 20, inclusão de run sem relatório e
  exclusão por TTL de sete dias. Nenhuma jornada ASI foi iniciada.
