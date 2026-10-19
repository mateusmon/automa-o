## Sprint 18 — diagnóstico de erros internos da GUI v2

- [x] **Gate Sol G18 — contrato do registro e consulta de erros internos.** Escopo restrito
  à `gui_v2/`; não alterar GUI antiga, engines, lançadores ou configuração compartilhada.
  A saída de Pytest/Sentinela continua em seus fluxos atuais e não deve ser copiada para o log
  interno da interface.

  **Contrato de captura e logging:** configurar um logger nomeado sob `gui_v2`, com handler de
  arquivo próprio e sem propagar para o root, em `gui_v2/logs/`. Instalar a configuração antes
  da criação dos controladores/widgets. Registrar exceções não tratadas de callbacks Tk pelo
  ponto de extensão da janela, além das exceções globais de thread e do processo quando
  aplicáveis. Preservar os hooks anteriores; registrar cada falha uma vez, com timestamp,
  nível, origem e traceback. Callback Tk deve continuar seguindo o comportamento normal do Tk
  após o registro. Erro no próprio logging não pode chamar o logger novamente nem impedir a
  abertura/continuidade da interface.

  O arquivo deve usar UTF-8 e rotação limitada. Proposta inicial para implementação: 1 MiB por
  arquivo e até 5 cópias rotacionadas; confirmar que é suficiente ao limitar a exposição a
  erros e tracebacks, sem coletar saída de execução. Resolver o diretório a partir da localização
  da aplicação, nunca do diretório de trabalho corrente. Se `gui_v2/logs/` não puder ser criado
  ou escrito, manter a GUI disponível e emitir aviso de fallback sem modal repetitivo; o destino
  alternativo deve ser definido somente se a inspeção da distribuição demonstrar que é
  necessário, sem escrever fora do escopo autorizado por conveniência.

  **Contrato de leitura e sinalização:** a consulta apresenta registros do arquivo interno,
  separados da Execução/Sentinela, com estado vazio e traceback legível. O indicador em
  Configurações sinaliza registro mais recente ainda não consultado; abrir a consulta marca o
  conjunto atual como visto. Preferir derivar esse estado do offset/timestamp já exibido ou de
  estado local mínimo, sem ampliar `preferences.local.json` antes de demonstrar necessidade.
  Falha de leitura/arquivo inválido deve aparecer como estado de diagnóstico indisponível, sem
  derrubar a janela.

  **Arquivos previstos:** novo serviço em `gui_v2/services/` para configuração/leitura;
  `gui_v2/app.py` para inicialização e ligação dos callbacks; `gui_v2/pages/settings_page.py`
  e, se necessário, componente próprio para a consulta; `gui_v2/components/sidebar.py` apenas
  para o marcador. Confirmar no S18.1 após inspeção da distribuição e do ciclo de vida real.

  **Riscos/invariantes:** não duplicar ao encadear hooks; não substituir silenciosamente hooks
  usados pelo ambiente de desenvolvimento; não criar recursão se o disco falhar; não capturar
  texto de processos filhos; manter Tk na thread principal; não registrar credenciais ou dados
  de teste sem necessidade; preservar os logs de execução existentes.

  **Verificação prevista:** serviço sem janela para formato, traceback, rotação, leitura e falha
  de I/O; exceções simuladas para callback, thread e hook global sem duplicidade; smoke com
  widgets Tk reais para estado vazio, chegada/consulta de erro e marcador; inspeção do atalho
  sem terminal se o ambiente permitir. Não executar automações ASI nem processos de teste para
  validar este recurso.

- [x] **S18.1 — fundação do registro e leitura local.** Novo serviço
  `gui_v2/services/gui_error_service.py` configura o logger `gui_v2` antes de preferências,
  controladores e widgets, sem propagação para o logger root. O arquivo
  `gui_v2/logs/gui_errors.log` usa UTF-8 e rotação de 1 MiB com cinco cópias. A leitura agrega
  as cópias em ordem cronológica e retorna conteúdo ou estado indisponível para falha de
  configuração/leitura. Falhas de escrita atualizam o estado do serviço e emitem no máximo um
  aviso, sem chamar o logger recursivamente. O serviço expõe o logger para os hooks da etapa
  seguinte. `gui_v2/app.py` inicializa o serviço antes de criar a janela. A regra local
  `svn:ignore` de `gui_v2` agora inclui `logs`, preservando as entradas existentes.

  Verificação: compilação sintática de `app.py` e `gui_error_service.py`; revisão estática de
  caminhos e contratos. Não rodei testes de serviço nem abri a GUI nesta microsprint.

- [x] **S18.2 — captura de exceções não tratadas.** `App.report_callback_exception()` registra
  falhas dos callbacks Tk e delega ao comportamento padrão para preservar a saída de
  desenvolvimento. `GuiErrorService` instala hooks de processo e thread que registram exceções
  `Exception`, encadeiam os handlers anteriores e evitam encadear o próprio hook em instalações
  repetidas. Ao fechar normalmente, a GUI restaura os hooks anteriores somente se ainda for dona
  deles. Falhas no registro não substituem nem interrompem o tratamento original. Nenhum
  visualizador/indicador foi incluído.

  Verificação: compilação sintática e importação dos módulos alterados. Não rodei testes nem
  abri a GUI; o comportamento real dos callbacks Tk permanece para validação manual.

- [x] **S18.3 — consulta visual nas Configurações.** A terceira aba “Erros da GUI” lê o
  histórico interno sem misturar stdout/stderr do Pytest ou da Sentinela. Mostra estado vazio,
  erro de leitura em destaque ou tracebacks em caixa rolável somente leitura. Inclui Atualizar
  para reler o arquivo e Copiar tudo para compartilhar o conteúdo carregado. A aba ainda não
  tem indicador de registros novos/não vistos.

  Verificação: compilação sintática e importação dos módulos alterados passaram. Não abri a GUI;
  dimensões, legibilidade e cópia com widgets reais ainda precisam de smoke visual manual.

- [x] **S18.4 — marcador de erros não vistos.** Um ponto discreto aparece ao lado de
  Configurações quando a assinatura dos logs difere da última consulta. A assinatura vista é
  guardada em `gui_v2/logs/gui_errors_seen.txt`, separada das preferências. Ao selecionar
  “Erros da GUI”, a tela relê e marca o conjunto consultado; enquanto essa aba estiver aberta,
  a checagem periódica atualiza conteúdo e estado quando chegar outro registro. Nenhuma ação
  de limpeza do histórico foi adicionada.

  Verificação: compilação sintática e importação dos módulos alterados passaram. Não abri a
  GUI; o posicionamento visual do ponto e o fluxo com widgets reais permanecem pendentes de
  smoke manual.

- [x] **S18.5 — revisão final e smoke do ciclo.** Revisão estática confirmou a assinatura
  persistida separadamente das preferências, a atualização pela seleção da aba e pela checagem
  periódica, e o agendamento/cancelamento da checagem no ciclo de vida da janela. A revisão do
  CustomTkinter revelou que o callback da aba é chamado sem argumentos; a assinatura de
  `SettingsPage._on_settings_tab_changed()` foi corrigida para consultar a aba no widget.

  Verificação do serviço: smoke isolado com arquivos temporários confirmou estado vazio, registro
  de erro, indicador não visto, marcação da assinatura consultada e detecção de um erro posterior.
  Compilação sintática e importações também passaram.

  Smoke funcional com widgets Tk reais, fora do sandbox: passou o estado vazio, a captura de
  exceção não tratada de callback com traceback, o ponto dentro da barra lateral, a consulta da
  aba, a marcação como visto, a chegada de outro erro com a aba aberta e o fechamento da janela.
  A persistência do estado visto após recriar o serviço também passou. Os logs desse smoke
  ficaram em diretórios temporários removidos ao final.

  A validação de borda confirmou rotação limitada a 1 MiB por arquivo e cinco cópias, retenção
  do registro mais recente, instalação repetida dos hooks de processo/thread sem duplicidade e
  encadeamento do handler anterior uma vez. Arquivo UTF-8 inválido, caminho bloqueado e falha
  simulada na escrita retornaram diagnóstico indisponível sem derrubar a GUI. Os hooks agora
  deixam de tentar registrar quando o serviço está indisponível, evitando que o fallback do
  Python envie outra cópia para `stderr`. O callback de “Copiar tudo” também foi exercitado com
  widgets reais e coletor substituto, sem acessar a área de transferência do usuário.

  Validação visual na janela real, via controle nativo do Windows: a aba vazia ficou legível;
  “Atualizar” preservou o estado vazio e “Copiar tudo” permaneceu desabilitado. Um registro de
  teste apareceu automaticamente com a aba aberta. Um segundo registro, criado enquanto “Geral”
  estava aberta, acendeu o ponto vermelho em Configurações; ao abrir “Erros da GUI”, o registro
  apareceu e o ponto sumiu. Os dois registros foram removidos após confirmar que o arquivo
  continha apenas os marcadores de teste, e a tela voltou ao estado vazio.

  A inspeção revelou que a coluna reservada ao ponto cortava o nome e a descrição da marca na
  barra lateral. A marca e o bloco de status passaram a ocupar as duas colunas. Uma segunda
  instância confirmou visualmente ambos os textos inteiros e a aba de erros; ela foi fechada,
  preservando a janela original do usuário.
