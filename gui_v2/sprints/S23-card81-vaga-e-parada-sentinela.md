# Sprint 23 — reutilização de vaga e parada seletiva da Sentinela

Card Trello: [#81 — Permitir o início de outro processo da Sentinela quando um deles já tiver finalizado](https://trello.com/c/N3HC2jkP)

## Objetivo e limites

Permitir que uma nova jornada comece quando somente uma das duas execuções estiver ativa e
oferecer uma escolha clara entre parar uma execução e parar todas. Preservar o limite fixo de
duas execuções simultâneas, os IDs, supervisores, relatórios, logs, traces e controles próprios
de cada run. Não criar fila, terceira vaga nem alterar a engine da Sentinela sem necessidade
demonstrada.

O card mostra uma jornada `RUNNING` e outra `SUCCEEDED`, enquanto o painel de jornadas e o botão
Iniciar permanecem bloqueados. Não há comentários ou cards vinculados indicados pelo conector;
o card tem uma captura de tela. A escolha de parada individual ou conjunta foi acrescentada pelo
usuário nesta conversa.

**Regra proposta para confirmação antes da implementação:** enquanto houver uma execução ativa,
cliente e modo permanecem fixos. A vaga livre permite preparar uma nova jornada desse cliente.
A seleção do próximo início é independente dos registros já iniciados; uma jornada ainda ativa
não pode ser iniciada novamente. Confirmar com o usuário caso a troca de cliente ou de modo
durante uma execução também deva ser permitida.

## S23.1 — Fechar o contrato e reproduzir os estados

- [x] Registrar a matriz de estados para zero, uma e duas vagas ocupadas, incluindo `STARTING`,
  `RUNNING`, `PAUSE_REQUESTED`, `PAUSED_BETWEEN_TESTS`, `STOPPING` e estados terminais.
- [x] Reproduzir os estados de duas execuções, uma vaga livre, escolha de próxima jornada e
  bloqueio do alvo ativo na GUI real, sem interferir nas execuções do usuário. Conferir parada,
  fechamento e restauração da página.
- [x] Identificar os campos de lote ainda compartilhados no controlador e definir como preservar
  seu acompanhamento quando uma nova partida ocorrer antes do término da execução anterior.

Matriz confirmada: `STARTING`, `RUNNING`, `PAUSE_REQUESTED`, `PAUSED_BETWEEN_TESTS` e `STOPPING`
ocupam uma vaga. Uma execução terminal (`SUCCEEDED`, `FAILED`, `SKIPPED` ou `INTERRUPTED`) libera
a vaga depois que o supervisor conclui o processo e o registro deixa de estar ativo.

| Execuções que ocupam vaga | Vagas livres | Seleção e início |
|---:|---:|---|
| 0 | 2 | Até duas jornadas distintas |
| 1 | 1 | Uma jornada diferente da que segue ativa |
| 2 | 0 | Seleção e início bloqueados |

Enquanto há execução ativa, cliente e modo permanecem fixos. `_plans` contém apenas a próxima
seleção e é limpo depois de iniciar; `_selected_execution_id` aponta a visualização atual;
`_run_artifact_ids` agrega as saídas das execuções deste ciclo; `_stop_requested_ids` evita
pedidos duplicados; `_stop_completion_events` acompanha o encerramento das árvores.

**Aceite:** contrato de ocupação/liberação de vaga e de seleção documentado antes de alterar
o código. A vaga só fica livre após o encerramento efetivo do processo e sua finalização no
registro; pausa e parada em andamento ainda ocupam vaga.

## S23.2 — Permitir nova partida com uma vaga livre

- [x] Ajustar a guarda do controlador para aceitar somente a quantidade de novos processos que
  cabe nas vagas livres, com revalidação imediatamente antes de criar os supervisores.
- [x] Preservar o estado e os eventos de todas as execuções anteriores ao iniciar uma nova;
  não limpar pedidos de parada nem sobrescrever o acompanhamento de lotes pendentes.
- [x] Manter a validação de alvo distinto, cliente/modo acordados, catálogo e demais contratos
  vigentes. Recusar uma seleção de duas jornadas quando houver só uma vaga.

**Aceite:** duas execuções ocupam as duas vagas; quando uma chega ao terminal, uma terceira
partida histórica pode ocupar a vaga liberada sem passar de duas ativas em nenhum instante.
Logs, resultados e parada da execução sobrevivente continuam associados ao seu `execution_id`.

## S23.3 — Ajustar seleção e apresentação da GUI

- [x] Separar a seleção do próximo início dos registros já iniciados. Exibir quantas vagas
  estão disponíveis e uma mensagem de bloqueio compreensível quando não houver capacidade.
- [x] Habilitar as jornadas elegíveis e Iniciar quando existir vaga e uma seleção válida;
  bloquear a jornada que ainda está ativa e impedir que a seleção visual antiga provoque
  reinício acidental. Preservar a visualização de histórico, logs, relatório, pasta e traces.
- [x] Ajustar o leiaute somente se a distinção entre próxima jornada e execuções em andamento
  não ficar clara na estrutura atual. Conferir largura mínima, rolagem e textos extensos.

Na captura em 1024 px, a jornada ativa, a vaga livre e a próxima seleção continuam distinguíveis;
os paths da prévia quebram em linhas. O título da prévia é cortado no fim, mas o total de
ocorrências aparece completo dentro da própria prévia.

**Aceite:** o usuário identifica qual jornada será iniciada, quais estão em andamento e qual
registro está selecionado para ver resultados ou aplicar controles.

## S23.4 — Escolha de parada e validação funcional local

- [x] Com duas execuções ativas, oferecer ações explícitas para parar uma execução identificada
  por alvo/ID ou parar as duas; permitir cancelar sem efeito. Se o seletor apontar para um run
  concluído ou histórico, apresentar as ativas para escolha, sem agir sobre o registro antigo.
- [x] Com uma execução ativa, oferecer a parada dessa execução. Desabilitar ações de parada
  inadequadas durante `STOPPING`, preservando a possibilidade de parar a outra ativa.
- [x] Reutilizar a parada por `execution_id` e o caminho existente de parar todas. O fechamento
  da GUI continua a pedir confirmação e a aguardar todas as árvores ativas.
- [x] Validar com o Python do `.venv` capacidade, parada e isolamento usando processos locais
  controlados; abrir a GUI real, testar callbacks Tk, histórico e restauração, e capturar estados
  normais e de borda. Registrar separadamente a integração ASI não executada.
- [x] Confirmar que pausa e `STOPPING` ocupam vaga e que apenas estados terminais liberam capacidade.

**Aceite:** uma parada individual não atinge a irmã; a parada conjunta alcança apenas as
execuções ativas registradas; uma vaga em `STOPPING` não é reutilizada prematuramente.

## S23.5 — Revisão crítica independente e encerramento

- [x] Rodar um agente crítico independente para revisar requisitos, diff, limites do card,
  concorrência, eventos tardios, seleção, relatórios, parada, interface e dívida introduzida.
- [x] Corrigir achados concretos, repetir somente as verificações afetadas e confirmar o escopo
  com `svn status` e `svn diff`, preservando alterações locais preexistentes.
- [x] Conferir os logs da GUI antes/depois e fechar a aplicação pelo caminho normal
  `App._request_close()`. Relatar o que foi provado com código, Tk real, capturas e, se houver,
  execução ASI; explicitar o que não foi rodado.
- [x] Registrar que a execução PCDF deixou de ser exigida pelo usuário; a jornada curta TRE-PE
  foi executada e aprovada, conforme a evidência abaixo.

**Aceite final:** o card 81 e a escolha de parada funcionam com até duas execuções ativas,
sem perda de isolamento ou regressão observada. A conclusão depende das evidências obtidas,
não apenas de compilação ou de código de saída zero.

## Gate e situação de execução

O usuário aprovou a implementação. Usar as etapas abaixo para registrar o progresso e só marcar
aceite quando a evidência correspondente existir. Não editar `contexto-web/PROJECT_CONTEXT.md`
sem pedido explícito.

### Retomada — 15/10/2026

O usuário pediu que o Codex continuasse após a pausa anterior. A revisão crítica final e as
verificações locais foram concluídas. A tentativa de integração na PCDF foi bloqueada por senha
expirada; o aceite de execução real na PCDF permanece pendente. A pedido do usuário, a jornada
equivalente foi executada no TRE-PE e passou integralmente.

### Implementado no working copy

- `gui_v2/controllers/sentinel_controller.py`: nova partida de uma jornada com uma vaga livre;
  limite de duas execuções ativas; alvo ainda ativo não pode partir de novo; os IDs dos lotes
  anteriores e os pedidos de parada são preservados; `request_stop()` consulta as ativas e
  permite escolher uma ou todas. Cliente e modo ficam fixos enquanto há execução ativa.
- `gui_v2/pages/sentinel_page.py`: mostra a capacidade livre, permite selecionar e expandir
  jornadas elegíveis com uma vaga, bloqueia o alvo já ativo e oferece diálogo com ações por
  execução, “Parar as duas” e “Cancelar”. A seleção de histórico continua independente.
- A revisão crítica independente encontrou um bloqueio na expansão com uma vaga; a guarda de
  `_toggle_expansion()` foi corrigida. A revisão estática posterior não encontrou outro defeito
  comprovado, mas pediu validação final da GUI e do fechamento.
- Na revisão crítica final, a prontidão da próxima jornada também foi corrigida nos ciclos de
  polling, término natural e término após `STOPPING`. O agente revisou novamente o diff completo
  e liberou a validação PCDF, sem novos achados comprovados.

### Evidência obtida e limite da validação

- O Python do `.venv` abriu a GUI real fora do sandbox. Houve captura de duas ativas, uma vaga
  livre, diálogo de parada, largura mínima e expansão em
  `gui_v2/sprints/evidencias/card81/01-duas-ativas.png` a `05-expansao-vaga-livre.png`.
- O teste isolado do controlador com serviços simulados passou pelo ciclo duas ativas → uma
  concluída → terceira partida, preservação de IDs e encaminhamento da parada individual/conjunta.
- Três processos Python locais, supervisionados por `SentinelExecutionService`, confirmaram:
  limite de duas vagas; rejeição de uma terceira durante `STOPPING`; parar uma execução mantém
  a irmã viva; e a vaga só é reutilizada depois da saída e do estado terminal.
- Um teste Tk confirmou os callbacks de parar uma, parar as duas e cancelar, inclusive com uma
  única execução. Outro confirmou que uma seleção histórica não redireciona a parada e que a
  execução ativa continua acessível enquanto a irmã está em `STOPPING`.
- A página preservou sua instância, capacidade e bloqueio do alvo ativo ao alternar para outra
  tela e restaurar a Sentinela. `App._request_close()` também percorreu confirmação e parada até
  fechar a janela, com o resultado do supervisor controlado pelo harness.
- `.venv\Scripts\python.exe -B -m py_compile` passou para `sentinel_controller.py` e
  `sentinel_page.py`.
- Um harness com o `.venv` confirmou que o estado de prontidão sobrevive a dez ciclos do polling
  e que, após uma execução em `STOPPING` terminar, a próxima jornada volta a aparecer como pronta.
- A primeira automação de cliques Tk falhou ao localizar texto acentuado e registrou duas
  exceções de callback em `gui_v2/logs/gui_errors.log` (1.151 bytes). As validações posteriores
  corrigiram o harness e passaram sem adicionar linhas; o log continua com apenas aquelas duas
  exceções de teste. Os callbacks foram acionados por `.invoke()` em widgets Tk; a captura real
  do diálogo confirma o leiaute visual.
- O diff foi conferido e não inclui `historico_testes/estado_atual/pcdf.json`, que já estava
  modificado antes desta tarefa. As cinco capturas foram adicionadas com `svn add --parents`
  e estão agendadas para inclusão no próximo commit; ainda não houve commit.
- A tentativa de integração atualizou `historico_testes/estado_atual/pcdfv4.json`; esse estado
  foi preservado junto dos relatórios de falha gerados pela tentativa.
- A pedido do usuário, a mesma jornada de inventário foi executada no TRE-PE (`--cliente trepe`):
  os testes de formação, consulta, alteração e exclusão passaram, sem falhas, skips ou retentativas
  em 47 segundos. Relatório: `sentinela/reports/2026-10-15_10h08_trepe_patrimonio_inventario/report.html`.
- A execução bem-sucedida atualizou `historico_testes/estado_atual/trepe.json`; a alteração foi
  preservada.

### Revisão posterior do controller — 15/10/2026

- A recriação da página sobrescrevia a mensagem de próxima jornada pronta, tanto com uma execução
  ativa quanto depois de um término. `create_page()` agora preserva o status gerado pelo plano.
- A parada individual informava a quantidade de vagas ocupadas como se todas estivessem parando;
  o polling também substituía o aviso de interrupção após 100 ms. A contagem e o status agora
  consideram somente registros em `STOPPING`.
- Um pedido de parada sem modo confirmado pelo supervisor podia exibir “concluída com sucesso”
  enquanto o registro era marcado `INTERRUPTED`. O estado terminal agora usa somente os modos
  `graceful` e `forced` para afirmar interrupção; nos demais casos usa código de saída e relatório.
- O controlador não usa `_close_waiters` nem o indicador `_close_requested`; ambos foram removidos.
  O fechamento continua a usar `_stop_completion_events` e `wait_for_stop()`.
- Harnesses do `.venv` cobriram recriação com e sem execução ativa, parada individual com outra
  jornada em andamento, polling e classificação do resultado com parada confirmada ou não.
  Tk real preservou “Uma jornada pronta para execução” e “1 vaga livre” após recriar a página e
  aguardar 450 ms. Captura: `gui_v2/sprints/evidencias/card81/06-controller-restauracao.png`.
  `gui_errors.log` não recebeu novas linhas; o fechamento usou `App._request_close()`. Um processo
  Python local supervisionado também confirmou que `stop_all_and_wait()` aguarda a árvore,
  finaliza o registro como `INTERRUPTED` e libera a vaga.
- Esta revisão alterou `sentinel_controller.py`, este registro de sprint e a captura 06; a análise
  aprofundada de `sentinel_page.py` ficou para a solicitação seguinte do usuário.
- A captura enviada pelo usuário durante a primeira validação mostrou esse diálogo de teste
  com IDs fictícios `11111111` e `22222222` sobre um registro histórico.

### Revisão posterior da página — 15/10/2026

- A jornada ativa podia ser um nó pai da árvore. Seu botão de expansão era desabilitado junto
  com o de seleção, impedindo alcançar jornadas filhas com a vaga restante. A expansão agora
  permanece disponível; apenas selecionar um alvo ativo ou iniciar sem vaga é bloqueado.
- `set_running(True)` podia reabilitar Parar após `set_execution_records()` desabilitá-lo para
  uma execução em `STOPPING`, inclusive na recriação da página. O estado de Parar agora vem
  apenas dos registros paráveis; a lista vazia também o desabilita.
- O Python do `.venv` exercitou esses estados em widgets Tk reais: árvore com alvo pai ativo,
  seleção da filha e prontidão de Iniciar com uma vaga, duas vagas ocupadas, transição
  `RUNNING` → `STOPPING`, troca de `set_running()` e lista vazia. Tudo passou. Captura:
  `gui_v2/sprints/evidencias/card81/07-page-arvore-ativa.png`. A captura foi inspecionada;
  `gui_errors.log` permaneceu em 1.151 bytes. `py_compile` da página passou.
- Esta revisão ficou restrita a `sentinel_page.py`, este registro e a captura 07. A jornada
  TRE-PE citada acima ocorreu antes destas correções de interface; não houve nova execução ASI.

### Limites registrados

- A jornada de inventário foi iniciada por engano com a chave `pcdfv4` (v4), não `pcdf` (v3).
  A configuração v4 aponta para `pcdfqas.linkdata.com.br:8080`; os dois primeiros testes
  falharam no login porque o sistema informou que a senha expirou. Cada teste fez três tentativas
  de login; a execução foi interrompida ao iniciar o terceiro teste. Nenhum dos dois primeiros
  alcançou o fluxo de negócio, portanto não houve validação funcional no ASI. O log também avisa
  que dois testes do catálogo não estão em `ordem.yaml`.
- A configuração PCDF v3 usa o mesmo host QAS e o mesmo par de credenciais de teste da PCDF v4.
  Não foi repetido o login com `pcdf`, pois a recusa da senha já ocorreu seis vezes e o contrato
  de login do projeto limita tentativas para evitar bloqueio da conta. Para concluir a integração,
  é preciso atualizar a senha pelo processo seguro do cliente e então executar o módulo
  `tests/patrimonio/inventario` com a chave `pcdf`.
- O fechamento com processo ativo foi exercitado no caminho real da GUI, mas o retorno do
  supervisor foi simulado nesse teste; encerramento de processo real foi validado separadamente
  com os três processos Python locais.
- `historico_testes/estado_atual/pcdf.json` já estava modificado antes desta tarefa e foi
  preservado.
