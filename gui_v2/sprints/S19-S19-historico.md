## Sprint 19 — menu lateral recolhível

- [x] **Gate Sol G19 — contrato da sidebar recolhível.** Escopo restrito à `gui_v2/`; não
  alterar a GUI antiga, engines, lançadores ou configuração compartilhada.

  **Comportamento pedido no card:** incluir um controle visível para alternar a sidebar entre
  expandida e compacta. A mudança deve ser instantânea, sem animação. No modo compacto, os
  ícones de navegação continuam visíveis e os textos deixam de ocupar espaço. A área de
  conteúdo deve acompanhar a largura liberada. A escolha permanece salva entre aberturas da
  GUI. O Gate libera somente S19.1–S19.4.

  **Direção de implementação:** manter a sidebar como um único componente e alternar sua
  largura e a apresentação dos widgets existentes, sem recriar páginas nem perder estado da
  página atual. O controle será o primeiro ícone no topo da navegação e não terá texto. Seu
  desenho será um contorno quadrado com uma divisória vertical central, no mesmo estilo e paleta
  dos ícones atuais. No modo compacto, ocultar a marca ASI inteira para que não fique cortada;
  manter visíveis o controle, os ícones de navegação e o indicador de erro. Verificar como
  representar o estado do ambiente no rodapé sem texto cortado. A decisão de S19.1 fixa largura
  compacta de 72 px. No desenho inicial da S19.1, a marca quadrada de 48 px seria mantida com
  margens reduzidas e a seta ficaria após a navegação. As capturas da S19.2 revelaram o corte da
  marca e a posição isolada do texto; o feedback do usuário substitui essas duas escolhas em
  S19.3 pela marca oculta e o ícone de painel no topo. A coluna do marcador fica com seus 20 px
  mínimos ao reduzir sua margem direita de 14 px para 4 px. Sobram 52 px para os botões; margem
  externa de 4 px deixa 44 px. O `CTkButton` mantém padding horizontal mínimo de 10 px por lado
  (o raio do canto prevalece sobre `border_spacing=8`), então o ícone de 20 px cabe em 40 px.
  O rodapé conserva somente o ponto verde de ambiente.

  Persistir `sidebar_collapsed` no `GuiPreferences` e no arquivo local já usado pelo serviço de
  preferências. Tratar campo ausente ou inválido como expandido, preservando os arquivos de
  preferências existentes. Como o campo é aditivo e pode ser lido com padrão em arquivos v3,
  manter `schema_version` em 3, salvo se a inspeção de compatibilidade mostrar que o contrato
  atual exige incremento.

  **Arquivos previstos:** `gui_v2/components/sidebar.py`,
  `gui_v2/services/preferences_service.py`, `gui_v2/app.py` e `gui_v2/assets.py`; atualizar este registro e o índice
  `gui_v2/SPRINTS.md`. Não editar `PROJECT_CONTEXT.md` sem pedido explícito.

  **Critérios de aceite:**
  - O controle expande/recolhe a sidebar imediatamente, sem animação.
  - No modo compacto, os três ícones, seleção da página e indicador de erro continuam legíveis.
  - O controle é apenas o ícone de painel dividido e aparece antes dos três itens de navegação.
  - A marca ASI fica oculta no modo compacto e não aparece cortada.
  - O conteúdo da página usa o espaço adicional e volta ao layout anterior ao expandir.
  - A alternância não troca a página nem apaga o estado dos widgets nela.
  - A preferência persiste ao fechar e abrir a aplicação; arquivo antigo, campo ausente ou valor
    inválido inicia expandido.
  - Tema claro/escuro e cores de destaque continuam aplicados nos dois modos.

  **Verificação prevista para a execução:** inspeção do diff e validação do carregamento/salvamento
  da preferência; smoke com widgets Tk reais em ambas as larguras, alternância repetida,
  indicador de erro, ajuste do conteúdo, seleção e estado de página preservado; reiniciar com a
  preferência salva em cada modo. Não executar automações ASI nem processos de teste para
  validar este recurso.

- [x] **S19.1 — preferência e contrato de estado.** A inspeção de `Sidebar` e da janela
  mostrada pelo usuário confirmou largura expandida de 236 px e marca de 48 px. Definida largura
  compacta de 72 px, reduzindo as margens laterais da marca a 12 px; os botões de navegação usam
  a coluna principal, com margem de 4 px, ícone de 20 px e `border_spacing=8`; reduzir para 4 px
  a margem direita do indicador, mantendo a coluna mínima de 20 px. O controle de alternância
  terá uma linha própria após as páginas, com seta; o rodapé mantém apenas o indicador verde.
  `GuiPreferences.sidebar_collapsed` foi adicionado
  como campo opcional, padrão `False`, sem incremento de schema. Falta confirmar esse arranjo
  visualmente com a marca oculta e o ícone no topo em S19.3.

  Verificação: smoke com `PreferencesService` confirmou padrão expandido, campo ausente/tipo
  inválido, round-trip para `True` e schema 3; `py_compile` passou. A tentativa de abrir a GUI
  dentro do sandbox falhou com `TclError: Can't find a usable init.tcl`; a abertura fora do
  sandbox com o Python do `.venv` foi validada em S19.2.
- [x] **S19.2 — alternância visual sem reconstrução.** `Sidebar.set_collapsed()` muda a largura
  entre 236 e 72 px, esconde/mostra os rótulos da marca e do rodapé, centraliza os ícones e
  mantém a coluna do indicador de erro. A linha de alternância usa seta e rótulo expandido; a
  página atual não é reconstruída. A alteração de largura foi síncrona.

  Validação visual fora do sandbox com o Python do `.venv`: expandir/recolher na janela real
  confirmou os três ícones, indicador vermelho, ponto verde, conteúdo ocupando o espaço liberado
  e Sentinela permanecendo selecionada nos dois estados. A captura revelou a marca cortada e a
  posição isolada do controle, corrigidas no planejamento de S19.3. Nenhuma execução foi
  iniciada. `py_compile` passou para `sidebar.py` e `preferences_service.py`.
- [x] **S19.3 — refino visual do controle e da marca.** Substituir `‹ Recolher`/`›` por um ícone
  vetorial quadrado com divisória vertical central, reutilizando a paleta e escala dos ícones de
  navegação. Movê-lo para a primeira posição no topo. No modo compacto, ocultar o frame da marca
  inteiro; ao expandir, restaurar marca e textos. Não recriar as páginas nem animar o redimensionamento.

  Validação: `py_compile` passou para `assets.py` e `sidebar.py`. Na janela real, o ícone de
  painel apareceu antes dos três itens; recolher removeu a marca por inteiro e manteve indicador
  de erro e ponto verde visíveis; expandir restaurou marca/textos sem corte. A largura mudou
  imediatamente, o conteúdo se ajustou e Sentinela permaneceu selecionada durante ambos os
  estados. Nenhuma execução foi iniciada. O tema escuro e a persistência ficam para S19.4.
- [x] **S19.4 — persistência e validação visual final.** A alternância
  agora carrega `sidebar_collapsed` na inicialização e salva cada mudança pelo serviço de
  preferências. O schema permanece v3; arquivo antigo, campo ausente ou inválido continua iniciando
  expandido.

  Validação executada: `compileall` nos módulos alterados; round-trip do serviço com arquivo
  temporário; smoke fora do sandbox com Tk real confirmou inicialização expandida, alternância
  nos dois sentidos, gravação de ambos os valores, página selecionada preservada e fechamento
  normal do event loop. Nenhuma execução ASI foi iniciada e `preferences.local.json` do usuário
  não foi tocado. O usuário confirmou a validação visual final da aplicação; com essa conferência,
  o layout e o comportamento ficaram aprovados nos temas claro e escuro. Sprint 19 concluída.
