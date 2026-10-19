# MCP ASI — controle do navegador para criação de testes

Servidor MCP que expõe o navegador (Playwright) ao agente, **reutilizando os
próprios flows/utils do projeto** (`login_flow`, `waits`, `escopo` v3/v4). Serve
para acelerar a criação de testes: abrir o sistema, logar em qualquer cliente,
navegar até uma página e **descobrir os seletores reais** dos campos.

## Por que existe

Criar um flow/teste exige conhecer os `name` dos inputs, o texto dos menus e o
comportamento de lookups. Este MCP permite fazer isso interativamente, sem
escrever scripts descartáveis: `inspecionar` devolve todos os
`input/select/button/radio/heading` da página (ou do iframe, na v4) com seus
atributos. Nas ferramentas que aceitam `escopo`, use `conteudo` (padrão) para o
formulário e `page` para elementos externos ao iframe da v4, como o cabeçalho e
o painel do usuário.

## Instalação

```bash
.venv\Scripts\python.exe -m pip install -r mcps/asi/requirements.txt
```

## Registro no Claude Code

O arquivo [`.mcp.json`](../../.mcp.json) na raiz registra os servidores MCP
(escopo de projeto):

- `asi-automacao` — este servidor custom (login ciente do cliente + inspeção dos
  seletores reais). Fica em `mcps/asi/`.
- `playwright` — o [Playwright MCP oficial](https://github.com/microsoft/playwright-mcp)
  (via `npx`), melhor para **explorar/navegar** o site de forma genérica
  (snapshot de acessibilidade, cliques, digitação). Requer Node/npx; no Windows
  nativo é lançado por `cmd /c npx`.
- `trello` — servidor custom para gerenciar cards do Trello (ver `mcps/trello/`).

Use o `playwright` para descobrir a estrutura e o `asi-automacao` para logar como
o projeto e extrair os `name=` dos campos na hora de escrever os flows.

Ao abrir o Claude Code na pasta do projeto, aprove os servidores quando
solicitado. Alternativa por CLI para o custom:

```bash
claude mcp add asi-automacao -- .venv/Scripts/python.exe mcps/asi/server.py
```

Se o caminho relativo não resolver na sua máquina, troque `command` em
`.mcp.json` pelo caminho absoluto do Python do venv.

## Ferramentas

| Ferramenta | O que faz |
| --- | --- |
| `iniciar_navegador(cliente, ambiente, headless, logar_auto)` | Abre o navegador e loga. `cliente` vazio = `cliente_ativo` do configs.yaml. Define a versão automaticamente. |
| `estado()` | Cliente, versão, URL e título atuais. |
| `ir_home()` | (v4) Volta para a tela de módulos. |
| `clicar_texto(texto, exato, indice)` | Clica por texto visível (módulos e itens de menu). |
| `clicar_role(role, nome, indice)` | Clica por role acessível (ex.: `link` / "Corporativo"). |
| `clicar_titulo(titulo)` | Clica por atributo `title` (ex.: "Abrir menu"). |
| `clicar_seletor(seletor, escopo)` | Clica por CSS no `conteudo` ou no `page` externo. |
| `inspecionar(escopo)` | **Lista os elementos interativos com seus `name`** no `conteudo` ou `page`. |
| `inspecionar_seletor(seletor, escopo)` | Inspeciona quantidade, texto, valor e visibilidade por CSS, inclusive de elementos ocultos. |
| `textos_visiveis(escopo)` | Lista textos curtos visíveis no `page` (padrão) ou no `conteudo`. |
| `preencher(seletor, valor)` | `fill` simples no escopo atual. |
| `preencher_lookup(seletor, valor)` | Lookup por código/nome via `preencher_campo` do projeto. |
| `marcar_radio(name, value)` | Marca radio por `name`+`value`. |
| `screenshot()` | Captura a tela (retorna imagem). |
| `fechar_navegador()` | Fecha o navegador. |

## Exemplo de uso (chegar ao formulário de UG na v4)

```
iniciar_navegador(cliente="pcdfv4")
ir_home()
clicar_texto("Corporativo")
clicar_titulo("Abrir menu")
clicar_texto("Estrutura Organizacional")
clicar_texto("UG - Unidade Gestora")
inspecionar()        # -> mostra cdUg, nmUg, cdCidade, sgUg, inAdmDireta, ...
```

Para a v3, a navegação usa `clicar_role("link", "Corporativo")` →
`clicar_role("link", "Estrutura Organizacional")` → `clicar_texto("UG - Unidade Gestora")`.

## Arquitetura

O Playwright síncrono é preso a uma thread. Todas as chamadas são despachadas a
uma thread trabalhadora dedicada (`PWWorker`), permitindo reutilizar com
segurança os flows síncronos do projeto.
