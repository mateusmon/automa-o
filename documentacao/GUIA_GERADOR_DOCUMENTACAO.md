# Guia do Gerador de Fluxogramas (gerar_documentacao.py)

Script autônomo que lê o código-fonte dos testes e dos flows do Genesis **sem executá-los** e
gera um site estático de fluxogramas Mermaid em `documentacao/fluxogramas/`. Serve para
enxergar o que cada teste faz, na ordem, sem abrir o arquivo `.py`.

Não roda teste, não abre navegador, não acessa banco. É só análise estática (`ast`) + HTML.

## 1. Como executar

```bash
python gerar_documentacao.py           # regenera tudo (testes + genesis + índice)
python gerar_documentacao.py testes    # somente os testes
python gerar_documentacao.py genesis   # somente os flows do Genesis
```

Depois é só abrir `documentacao/fluxogramas/index.html` no navegador.

Os caminhos são ancorados na pasta do próprio script (`Path(__file__).parent`), então pode ser
chamado de qualquer diretório.

## 2. O que ele produz

```text
documentacao/fluxogramas/
├── index.html              # Índice único, com abas Testes / Genesis e campo de busca
├── mermaid.min.js          # Opcional — ver seção 7
├── testes/                 # Espelha a árvore de tests/
│   ├── almoxarifado/...
│   ├── patrimonio/...
│   └── corporativo/...
└── genesis/                # Um HTML por flow, agrupado por rotina
    ├── garantir_ua.html
    └── ...
```

Uma página por arquivo de teste e uma por flow do Genesis. A pasta é gerada por completo a
cada execução (ver seção 8). O diretório `documentacao/fluxogramas/` carrega
`svn:ignore = *`, então **nada do que está dentro dele é versionado** — cada um gera a sua
cópia rodando o script.

## 3. Como os passos são extraídos dos testes

O gerador percorre a AST de cada função `test*` (mesmo critério de coleta do pytest, o glob
padrão `python_functions = test*`) e traduz cada construção em um nó do fluxograma:

| No código do teste | No fluxograma |
|---|---|
| `login(page, dados)` | caixa `[Login]` |
| `existe = selecionar_x(page)` | caixa `[Selecionar x]` |
| `if not existe: pytest.skip()` | losango + saída lateral `([Teste ignorado])` |
| `if x: ... else: ...` | losango com ramos **Sim/Não** que reconvergem |
| `for tipo in tipos:` | paralelogramo `[/Para cada tipos/]` com aresta de volta |
| `_criar_funcionario(page, x)` (helper do próprio arquivo) | sub-rotina `[[Criar funcionario]]` **expandida inline** |
| `assert cond, "msg"` | losango com saída de falha |
| `raise RuntimeError("...")` | terminal `([Erro: ...])` |

Detalhes que importam na leitura:

- **Helpers locais são expandidos**, não viram uma caixa opaca. Um `return` dentro do helper
  encerra só o helper — o fluxo volta ao chamador e reconverge, em vez de morrer ali.
- **Chamadas com ponto são ignoradas** (`page.wait_for_timeout`, `contexto_cliente.ug()`,
  `logger.info`). São ruído de infraestrutura, não passo de negócio.
- **Blocos `except` são ignorados** de propósito; `try` e `finally` são percorridos.
- Se um arquivo tiver mais de uma função `test*`, sai **um diagrama por função**, rotulado.

Quando nada é reconhecido, a página mostra um aviso amarelo em vez de um diagrama vazio —
normalmente significa que o teste não chama flows (ex.: `tests/test_dados.py`).

## 4. Genesis — rotinas vêm de `genesis/routines/`

A ordem dos flows do Genesis **não é mantida à mão dentro do script**. Ela é lida da AST de
`genesis/routines/*.py`: o gerador acha a função `run()`, pega as chamadas na ordem em que
aparecem e resolve cada uma para o arquivo-fonte pelos imports.

As duas formas de flow são resolvidas:

```text
from flows.garantir_ua.dispatcher import garantir_ua   ->  genesis/flows/garantir_ua/v3.py
from flows.garantir_uf_flow import garantir_uf         ->  genesis/flows/garantir_uf_flow.py
```

Consequência prática: **adicionou um flow numa rotina? Não precisa mexer no gerador.** Basta
rodar de novo. Flows que existem em `genesis/flows/` mas nenhuma rotina chama caem no grupo
amarelo "Sem rotina definida" no índice — é o jeito de descobrir flow esquecido.

O título de cada rotina vem de `_TITULO_ROTINA` no script (`link_user` → "Link User"). Rotina
nova sem entrada lá aparece com o nome do arquivo formatado.

Para pacotes versionados o gerador documenta o **`v3.py`** (cai para `v4.py` se não houver v3).

## 5. Índice e o catálogo da GUI

A aba **Testes** é ordenada e agrupada pelo `gui/catalog/modules_catalog.py` — mesma ordem de
módulo/seção que aparece na GUI. Teste que não está no catálogo vai para um bloco amarelo
`<Módulo> [Sem catalogo]` no fim. Isso é um efeito colateral útil: serve de conferência de
quem esqueceu de registrar o teste no catálogo.

A aba **Genesis** é agrupada por rotina, na ordem de execução real.

O campo de busca filtra a aba ativa por texto (nome do teste e nome do arquivo).

## 6. Registro de teste novo

Não há nada a fazer no gerador. Criou o teste em `tests/`, rodou o script, ele aparece.
Para ele cair no grupo certo do índice (e não no amarelo), registre no
`gui/catalog/modules_catalog.py` como manda o `CLAUDE.md`.

## 7. Mermaid — cópia local x CDN

As páginas precisam do `mermaid.js` para desenhar. O gerador escolhe sozinho:

- Se **`documentacao/fluxogramas/mermaid.min.js` existir**, as páginas apontam para ele por
  caminho relativo e funcionam offline.
- Se **não existir**, apontam para o CDN — e aí, sem internet, nenhum fluxograma renderiza
  (a página abre em branco, sem erro visível).

Para (re)criar a cópia local:

```bash
curl -o documentacao/fluxogramas/mermaid.min.js \
     https://cdnjs.cloudflare.com/ajax/libs/mermaid/10.6.1/mermaid.min.js
```

O arquivo sobrevive às regerações e não é versionado. Apagá-lo volta ao CDN automaticamente.

## 8. Limpeza da saída

`testes/` e `genesis/` são **apagados e recriados** a cada execução do modo correspondente.
É proposital: sem isso, teste renomeado ou removido deixava HTML órfão para sempre e o índice
continuava apontando para ele.

Por isso, rodando só `genesis`, o índice lista apenas os testes que ainda têm HTML da rodada
anterior — nunca gera link quebrado.

**Não guarde nada à mão dentro de `testes/` ou `genesis/`.** O `mermaid.min.js` fica um nível
acima justamente por isso.

## 9. Diagnóstico

O script imprime o que fez e avisa o que não conseguiu:

| Mensagem | Significado |
|---|---|
| `[ERRO] Nao foi possivel parsear <arquivo>` | erro de sintaxe no `.py` — a página sai vazia |
| `[AVISO] Catalogo nao encontrado` | índice de testes sai sem ordenação por módulo |
| `[AVISO] Rotinas do Genesis nao encontradas` | aba Genesis sai toda em "Sem rotina definida" |
| `[AVISO] Flow 'x' da rotina y sem fonte em disco` | a rotina importa um flow que não existe mais |
| `[AVISO] Dois flows chamados 'x'` | colisão de nome; só o primeiro é documentado |

## 10. O que NÃO fazer

- **Não hardcodar a lista de flows do Genesis no script.** Ela é derivada de
  `genesis/routines/*.py`. Uma lista fixa envelhece calada (foi exatamente o que aconteceu:
  o script listava `garantir_ug`, `garantir_ul_estoque` e `garantir_intervalo_patrimonial`,
  que não existem, e omitia todos os flows de arquivo único).
- **Não editar os HTMLs gerados** — a próxima execução apaga tudo.
- **Não tentar versionar o conteúdo de `documentacao/fluxogramas/`** — é saída gerada e o
  diretório já tem `svn:ignore = *`.
- **Não usar o fluxograma como fonte da verdade** para caminhos de erro: `except` não é
  desenhado, e `continue` vira nó terminal em vez de aresta de volta ao laço.
- Não confundir com o `documentacao/corporativo/` — aquilo é documentação escrita à mão do
  protocolo do módulo Corporativo, nada a ver com este gerador.
