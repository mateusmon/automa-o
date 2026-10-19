# Sprint 22 — rolagem consistente e inteligente na GUI v2

Card Trello: [#80 — Adicione scroll inteligente na GUI](https://trello.com/c/o0p9cANI)

## Objetivo

Investigar e corrigir os dois comportamentos de rolagem descritos no card: diferença de
velocidade entre a barra e o conteúdo, e mudança indesejada do alvo da roda em áreas
roláveis aninhadas quando o ponteiro permanece parado.

## S22.1 — Reproduzir e caracterizar a velocidade

- [x] Abrir a GUI v2 com `.venv\Scripts\python.exe -B -m gui_v2.main` e reproduzir o item 1
  do card na mesma área, comparando a roda sobre a barra e sobre o conteúdo.
- [x] Registrar página, widget, sistema operacional, deslocamento por evento e captura de tela.
- [x] Confirmar se a origem é o tratamento da roda do `CTkScrollbar` em relação ao
  `CTkScrollableFrame`; não generalizar o ajuste do catálogo sem evidência.

**Reprodução e causa:** na página Execução, catálogo de testes, a roda sobre o conteúdo e a
barra percorria distâncias diferentes. No CustomTkinter instalado, o `CTkScrollableFrame`
converte `event.delta` por 6 no Windows; o `CTkScrollbar` usa divisão por 40. Um evento
simulado de `delta=-120` agora produz a mesma fração `yview` em ambos os pontos.

## S22.2 — Corrigir e validar a velocidade

- [x] Após confirmar S22.1, ajustar a conversão no menor escopo que iguale a velocidade da
  roda sobre a barra e sobre o conteúdo.
- [x] Verificar roda para cima/baixo, scrollbar com thumb e trilho, limites do conteúdo e
  revisar a preservação do tratamento horizontal e de outros componentes sem relação.
- [x] Capturar a GUI após a correção e registrar os resultados observados.

## S22.3 — Reproduzir e caracterizar a rolagem aninhada

- [x] Identificar uma combinação real de contêiner externo e interno na GUI v2.
- [x] Reproduzir uma sequência contínua de eventos da roda iniciada fora do contêiner interno,
  com o ponteiro parado enquanto o conteúdo externo move o contêiner interno sob ele.
- [x] Registrar qual canvas recebe cada evento e se mover o ponteiro para dentro do contêiner
  interno muda o alvo conforme esperado.
- [x] Inspecionar os bindings e a lógica de seleção do alvo antes de escolher a solução.

## S22.4 — Corrigir e validar a rolagem aninhada

- [x] Após confirmar S22.3, manter o alvo da rolagem estável durante a sequência iniciada e
  recalculá-lo quando o ponteiro se mover, preservando a rolagem normal de cada área.
- [x] Validar rolagem iniciada no exterior, no interior, em limites de conteúdo e em páginas
  com mais de um contêiner; verificar a scrollbar arrastada e revisar os bindings de teclado.
- [x] Revisar vínculos globais de eventos e limpeza dos bindings para evitar efeitos entre
  páginas ou janelas.
- [x] Capturar evidências visuais e registrar qualquer comportamento não coberto.

## Revisão crítica e encerramento

- [x] Fazer revisão crítica independente da implementação e do escopo, procurando regressões,
  efeitos globais, dependências de APIs privadas do CustomTkinter e dívida técnica.
- [x] Executar validações solicitadas com o Python do `.venv`; comparar logs GUI antes/depois e
  fechar a aplicação por `App._request_close()`.
- [x] Registrar limitações do ambiente separadamente de falhas do código.

## Resultado local

- O card não identifica páginas, controles internos nem passos para reprodução.
- Não há comentários, anexos ou checklist no card; a consulta disponível não expôs vínculos
  com outros cards.
- `SmartScrollableFrame` concentra a escolha do alvo da roda nos quadros roláveis da GUI v2.
  Seu cache mantém o quadro de origem quando o conteúdo passa sob o ponteiro parado e muda
  o alvo quando a posição do ponteiro muda. A barra usa a mesma conversão do conteúdo.
- No teste visual da Execução, a página externa continuou rolando com o ponteiro parado quando
  o catálogo passou sob ele. Movendo o ponteiro para dentro, o catálogo rolou e a página
  externa ficou parada. Conteúdo e barra do catálogo alcançaram a mesma posição com uma roda
  de mesma intensidade. O arraste do thumb e o clique no trilho continuaram funcionando.
- Capturas: [início externo](evidencias/card80/01-externo-iniciado.jpg),
  [continuação externa](evidencias/card80/02-externo-continua-parado.jpg),
  [interno após mover ponteiro](evidencias/card80/03-interno-apos-mover-ponteiro.jpg),
  [barra no patch final](evidencias/card80/04-barra-patch-final.jpg).
- O Python do `.venv` carregou Tcl/Tk 8.6.15 e passou no smoke mínimo de inicialização.
- Smoke com widgets Tk reais verificou despacho dos bindings, igualdade de `yview` após roda
  sobre conteúdo/barra e isolamento entre janela principal e popup na mesma coordenada.
- A primeira abertura pelo terminal da ferramenta não expôs a janela para captura. A abertura
  pelo terminal integrado do VS Code permitiu a validação visual e o fechamento normal.
- A revisão crítica encontrou um risco entre janelas; o roteador passou a descartar eventos
  originados em outro `Toplevel`, e o teste com dois `Toplevel` confirmou o isolamento.
- Não surgiu `gui_v2/logs/gui_errors.log` durante as aberturas. Nenhuma execução ASI foi
  iniciada. Dependência de APIs privadas do CustomTkinter permanece e deve ser revisada ao
  atualizar essa biblioteca.
- A interação visual foi validada no Windows. Linux, macOS e navegação por teclado não foram
  exercitados na GUI; a implementação preserva os caminhos de conversão e bindings originais.

## Revisão complementar — popup e caixa de texto

- Uma revisão posterior identificou que a roda sobre a barra interrompia o binding global
  usado pelo `ClientPicker` para fechar o popup. A barra agora deixa o evento chegar a esse
  observador, enquanto o roteador evita rolagem duplicada. O seletor também reconhece o
  canvas da barra como parte da página hospedeira.
- Um smoke com widgets Tk reais reproduziu a rolagem simultânea da página e de um
  `CTkTextbox` sob o ponteiro parado. As caixas de texto da Execução e da Sentinela passaram
  a encaminhar a roda ao quadro original nessa situação; após mover o ponteiro, a caixa de
  texto volta a rolar normalmente. O smoke confirmou os dois estados e a igualdade de
  deslocamento entre conteúdo e barra.
- Na GUI visível, o popup de cliente fechou ao rolar a barra da página Execução, sem trocar
  a seleção. Capturas: [popup aberto antes da roda](evidencias/card80/05-popup-aberto-antes-barra.png)
  e [popup fechado após a roda](evidencias/card80/06-popup-fechado-apos-barra.png).
- A roda sobre a barra dos resultados do próprio popup também foi verificada. Ela revelou um
  fechamento indevido; o seletor passou a reconhecer essa barra como parte dos resultados.
  O smoke com `ClientPicker` real e a [captura da GUI](evidencias/card80/07-popup-interno-continua-aberto.png)
  confirmaram que a lista rola e o popup permanece aberto.
- A revisão crítica independente não encontrou outro defeito concreto. A integração com
  atributos privados do CustomTkinter segue como dependência de manutenção. A caixa de texto
  com conteúdo longo foi validada em widgets Tk reais, não na GUI completa.
