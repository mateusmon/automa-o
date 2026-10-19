# Guia de Testes — ASI Automação 2.0

Framework de automação E2E para o sistema ASI (Almoxarifado e Patrimônio), baseado em **Pytest + Playwright** com arquitetura data-driven e suporte nativo a múltiplas versões do GRP.

---

## Índice

1. [Arquitetura](#1-arquitetura)
2. [Sistema de dados](#2-sistema-de-dados)
3. [Convenções de testes e flows](#3-convenções-de-testes-e-flows)
4. [Catálogo da GUI](#4-catálogo-da-gui)
5. [Evidências e logs](#5-evidências-e-logs)
6. [Particularidades do ASI](#6-particularidades-do-asi)
7. [Suporte a múltiplas versões do GRP (v3/v4)](#7-suporte-a-múltiplas-versões-do-grp-v3v4)
8. [Histórico e estado de testes por cliente](#8-histórico-e-estado-de-testes-por-cliente)

---

## 1. Arquitetura

O projeto segue uma arquitetura em camadas com responsabilidades bem definidas:

```text
tests/     ← orquestração: "o que fazer" (cenários de alto nível)
flows/     ← interação UI: "como fazer" (ações no browser, versão-aware)
utils/     ← apoio técnico: esperas, logging, evidências, formatação
domain/    ← abstração de dados: ContextoCliente (dados do cliente)
```

### Responsabilidades por camada

| Camada | O que contém | O que NÃO contém |
| --- | --- | --- |
| `tests/` | Orquestração de flows, obtenção de dados via `contexto_cliente` | Cliques, `page.locator()` |
| `flows/` | Interação Playwright, esperas, lógica v3/v4 | Asserts de negócio, dados hardcoded |
| `utils/` | Funções genéricas reutilizáveis (waits, evidência, log, formatação) | Lógica de domínio ASI |
| `domain/` | `ContextoCliente` com métodos tipados de acesso a dados | Playwright, UI |

### Separação fundamental

- **Flows** encapsulam **uma única operação de UI** (navegar, preencher, consultar, selecionar, alterar, excluir).
- **Testes** orquestram flows em cenários completos.

Testes não tocam em seletores nem em lógica de UI. Flows não decidem se um teste deve ser pulado — eles retornam `bool` (ou `None`) e o teste toma a decisão.

### Estrutura de diretórios

```text
asi-automacao-2.0/
├── conftest.py                    # Fixtures Pytest centrais
├── pytest.ini                     # Configuração de markers e paths
│
├── configs/
│   ├── configs.yaml               # Clientes e ambientes (versionado)
│   └── configs.local.yaml         # Sobrescritas locais (não versionado)
│
├── genesis/                       # Engine de provisão de dados
│   ├── blueprint/                 # Dados de cada cliente (YAML)
│   ├── flows/                     # Flows de criação de dados (garantir_*)
│   ├── routines/                  # Rotinas por usuário (link_user, teste_user)
│   └── services/                  # Serviços de verificação (*_existe)
│
├── flows/                         # Flows de UI reutilizados pelos testes
│   ├── shared/                    # Flows transversais (login, logout, imprimir)
│   ├── almoxarifado/              # Flows por módulo ASI
│   └── patrimonio/
│
├── sentinela/                     # Engine que roda vários testes em uma ordem específica
│
├── tests/                         # Testes organizados por módulo ASI
│   ├── almoxarifado/
│   └── patrimonio/
│
├── utils/
│   ├── versao.py                  # get_versao(), set_versao(), escopo()
│   ├── waits.py                   # aguardar_ajax_global(), esperar_sucesso_ou_erro()
│   ├── evidencia.py               # screenshot(), registrar_pdf()
│   └── ...
│
└── domain/
    └── contexto_cliente.py        # ContextoCliente — acesso tipado a dados
```

### Fixtures principais (conftest.py)

| Fixture | Scope | O que faz |
| --- | --- | --- |
| `browser_session` | session | Instancia Chromium uma vez; reutilizado por todos os testes |
| `page` | function | Nova página + contexto por teste; captura screenshot em falha automaticamente |
| `contexto_cliente` | session | Lê `configs.yaml` + blueprint do cliente; retorna `ContextoCliente` pronto |

---

## 2. Sistema de dados

### Blueprint do cliente

> **Nota**: Atualmente usamos apenas uma blueprint para todos os clientes, chamada de `blueprint.yaml`. Nosso objetivo é usar somente uma para evitar ter de fazer ajustes específicos por cliente. As antigas ainda existem mas serão excluídas. Leia a seguinte instrução tendo em mente que este era o padrão antigo.

Cada cliente tem um arquivo `genesis/blueprint/<cliente>.yaml` com todos os dados de teste. Esse arquivo é a fonte única de verdade para os dados de cada cliente.

```yaml
dados_cliente:
  nome: "TSE"
  nomes: ["TSE", "Tribunal Superior Eleitoral"]   # variações para validar PDFs

unidade_gestora:
  codigo: "001001"
  nome: "SECRETARIA DE TECNOLOGIA DA INFORMAÇÃO"

almoxarifados:
  - sigla: "ALM-CENTRAL"
    nome: "Almoxarifado Central"

fornecedores:
  - codigo: "12345678000199"
    codigo_so_numeros: "12345678000199"
    nome: "PAPELARIA MODELO LTDA"

materiais:
  - nome: "PAPEL A4"
    complemento: "RESMA 500 FOLHAS"
    codigo: "000001"
    quantidade: "10"
    preco_unitario: "25,00"
    codigo_endereco: "A-01"

bens:
  - numero_patrimonial: "000001"
    descricao: "NOTEBOOK DELL"
    valor_aquisicao: "5000,00"
```

### API do ContextoCliente

`ContextoCliente` é a única forma de acessar dados de teste. Nunca use valores hardcoded.

```python
dados_cliente         = contexto_cliente.dados_cliente()           # dict com url, usuario, senha
ug                    = contexto_cliente.ug()                      # dict com codigo, nome
almoxarifado          = contexto_cliente.almoxarifado_padrao()     # primeiro da lista (determinístico)
almoxarifado          = contexto_cliente.almoxarifado_por_indice(1) # segundo da lista
material              = contexto_cliente.material_padrao()         # primeiro da lista
material              = contexto_cliente.material_qualquer()       # aleatório (cobertura ampla)
fornecedor            = contexto_cliente.fornecedor_padrao()       # primeiro da lista (determinístico)
bem                   = contexto_cliente.bem_padrao()              # primeiro da lista (determinístico)
```

Use `*_padrao()` para testes que precisam de previsibilidade; `*_qualquer()` para testes que cobrem cenários variados.

### Genesis — Provisão de dados

O Genesis garante que os dados do blueprint existem no ambiente antes dos testes rodarem. Ele é **idempotente**: pode ser executado múltiplas vezes sem duplicar dados.

```bash
python genesis/genesis_runner.py
```

### Checklist ao adicionar novo cliente

1. Registrar em `configs/configs.yaml` com `arquivo_dados` e `versao`.
2. Preencher ao menos um item válido por coleção exigida pelos testes que serão executados.
3. Configurar `ambientes` (`url`, `usuario`, `senha`).

### Falhas comuns de configuração

- `cliente_ativo` inexistente no YAML.
- `arquivo_dados` ausente ou caminho inválido.
- `ambiente` inexistente no cliente selecionado.
- `url`, `usuario` ou `senha` vazios para o ambiente escolhido.

---

## 3. Convenções de testes e flows

Este é o padrão que **todo** teste e flow novo deve seguir. Serve também como referência para refatoração de testes antigos.

### 3.1 Nomenclatura

#### Arquivos e funções

| Prefixo do arquivo | Nome da função | Operação |
| --- | --- | --- |
| `navegar_para_*_flow.py` | `acessar_*(page)` | Navegação de menus até a página |
| `preencher_*_flow.py` | `preencher_*(page, ...)` | Preenchimento de formulário |
| `consultar_*_flow.py` | `consultar_*(page, ...)` | Aplicar filtros de busca |
| `selecionar_*_flow.py` | `selecionar_*(page, ...)` | Selecionar linha no resultado |
| `alterar_*_flow.py` | `alterar_*(page, ...)` | Modificar campos de um registro aberto |
| `test_cadastro_*.py` | `test_cadastro_*(...)` | Teste de criação |
| `test_consulta_*.py` | `test_consulta_*(...)` | Teste de consulta/visualização |
| `test_alteracao_*.py` | `test_alteracao_*(...)` | Teste de alteração |
| `test_exclusao_*.py` | `test_exclusao_*(...)` | Teste de exclusão |

#### Retorno dos flows

| Tipo de flow | Retorna | Significado |
| --- | --- | --- |
| `navegar_para_*` / `acessar_*` | `None` | Lança exceção em falha |
| `preencher_*` | `None` | Lança exceção em falha via `esperar_sucesso_ou_erro` |
| `consultar_*` | `None` | Só aplica filtros — não seleciona |
| `selecionar_*` | `bool` | `True` = selecionou, `False` = não encontrou |
| `alterar_*` | `bool` ou `None` | `bool` quando pode ser inviável (ex.: campo desabilitado); `None` quando sempre possível |
| `verificar_*` | `bool` | `True` = condição satisfeita, `False` = não |

### 3.2 Estrutura de testes

Todos os testes seguem este esqueleto geral:

```text
login → navegar → [consultar → selecionar] → ação principal → [imprimir] → logout
```

#### Teste de Cadastro

Não importa `pytest` (não há skip). Chama `imprimir_relatorio` após cadastro bem-sucedido. O último flow de preenchimento faz o submit e valida o sucesso.

```python
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio
from flows.{modulo}.{submodulo}.navegar_para_*_flow import acessar_*
from flows.{modulo}.{submodulo}.preencher_dados_gerais_flow import preencher_dados_gerais
from flows.{modulo}.{submodulo}.preencher_*_flow import preencher_*


def test_cadastro_*(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Cadastro de <Nome com Capitalização de Título>.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    material = contexto_cliente.material_padrao()

    login(page, dados_cliente)
    acessar_*(page)
    preencher_dados_gerais(page, almoxarifado)
    preencher_*(page, material)  # último flow — faz submit e valida sucesso

    imprimir_relatorio(page)

    logout(page)
    logger.info("Finalizou teste de Cadastro de <Nome com Capitalização de Título>.")
```

#### Teste de Consulta

Importa `pytest`. Flows de consulta e seleção são sempre separados. Após seleção bem-sucedida, aguarda 5 segundos para visualização.

```python
import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout
from flows.{modulo}.{submodulo}.navegar_para_*_flow import acessar_*
from flows.{modulo}.{submodulo}.consultar_*_flow import consultar_*
from flows.{modulo}.{submodulo}.selecionar_*_flow import selecionar_*


def test_consulta_*(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Consulta de <Nome com Capitalização de Título>.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    material = contexto_cliente.material_padrao()

    login(page, dados_cliente)
    acessar_*(page)
    consultar_*(page, almoxarifado, material)
    existe = selecionar_*(page, almoxarifado)

    if not existe:
        logger.warning("Pulando teste.")
        pytest.skip()

    page.wait_for_timeout(timeout=5_000)

    logout(page)
    logger.info("Finalizou teste de Consulta de <Nome com Capitalização de Título>.")
```

#### Teste de Alteração

Mesmo padrão que consulta, com o flow de alteração após a seleção. O flow `alterar_*` pode retornar `bool` quando a alteração pode ser inviável.

```python
import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout
from flows.{modulo}.{submodulo}.navegar_para_*_flow import acessar_*
from flows.{modulo}.{submodulo}.consultar_*_flow import consultar_*
from flows.{modulo}.{submodulo}.selecionar_*_flow import selecionar_*
from flows.{modulo}.{submodulo}.alterar_*_flow import alterar_*


def test_alteracao_*(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou o teste de Alteração de <Nome com Capitalização de Título>.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    material = contexto_cliente.material_padrao()

    login(page, dados_cliente)
    acessar_*(page)
    consultar_*(page, almoxarifado, material)
    existe = selecionar_*(page, almoxarifado)

    if not existe:
        logger.warning("Pulando teste.")
        pytest.skip()

    alterou = alterar_*(page)  # omitir variável se o flow retorna None

    if not alterou:            # omitir bloco se o flow retorna None
        logger.warning("Pulando teste.")
        pytest.skip()

    logout(page)
    logger.info("Finalizou o teste de Alteração de <Nome com Capitalização de Título>.")
```

#### Teste de Exclusão

Usa o flow compartilhado `excluir_movimento`. Para almoxarifado, passar `esperar_sucesso=True`; para patrimônio, chamar sem parâmetros.

```python
import pytest
from loguru import logger
from playwright.sync_api import Page

from domain.contexto_cliente import ContextoCliente
from flows.shared.login_flow import login
from flows.shared.logout_flow import logout
from flows.shared.excluir_movimento_flow import excluir_movimento
from flows.{modulo}.{submodulo}.navegar_para_*_flow import acessar_*
from flows.{modulo}.{submodulo}.consultar_*_flow import consultar_*
from flows.{modulo}.{submodulo}.selecionar_*_flow import selecionar_*


def test_exclusao_*(page: Page, contexto_cliente: ContextoCliente) -> None:
    logger.info("Iniciou teste de Exclusão de <Nome com Capitalização de Título>.")

    dados_cliente = contexto_cliente.dados_cliente()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    material = contexto_cliente.material_padrao()

    login(page, dados_cliente)
    acessar_*(page)
    consultar_*(page, almoxarifado, material)
    existe = selecionar_*(page, almoxarifado)

    if not existe:
        logger.warning("Pulando teste.")
        pytest.skip()

    excluir_movimento(page, esperar_sucesso=True)  # True apenas para almoxarifado

    logout(page)
    logger.info("Finalizou teste de Exclusão de <Nome com Capitalização de Título>.")
```

### 3.3 Estrutura de flows

#### Flow de Navegação (`navegar_para_*`)

Divide internamente em `_v3` e `_v4`. A v4 usa `clicar_home_com_retry` e um loop com 2 tentativas para absorver falhas de carregamento.

```python
from loguru import logger
from playwright.sync_api import Page, expect

from utils.versao import get_versao
from utils.waits import aguardar_ajax_global, clicar_home_com_retry


def acessar_*(page: Page) -> None:
    logger.info("Iniciou navegação para <página>.")

    if get_versao() >= 4:
        _v4(page)
    else:
        _v3(page)

    logger.info("Finalizou navegação para <página>.")


def _v3(page: Page) -> None:
    page.get_by_role("link", name="Almoxarifado").click()  # ou "Patrimônio"
    page.get_by_role("link", name="Submenu").click()
    page.get_by_text("Nome da Página").click()
    aguardar_ajax_global(page)
    expect(page.get_by_role("heading", name="Título da Página")).to_be_visible()


def _v4(page: Page) -> None:
    for tentativa in range(2):
        try:
            clicar_home_com_retry(page)
            aguardar_ajax_global(page)

            page.get_by_text("Almoxarifado", exact=True).click()
            # ... demais cliques de menu ...
            aguardar_ajax_global(page)

            expect(page.get_by_role("heading", name="Título da Página")).to_be_visible()
            return

        except Exception as e:
            logger.warning("Navegação falhou na tentativa {}. Tentando novamente.", tentativa + 1)
            if tentativa == 1:
                raise RuntimeError(f"Falha ao concluir navegação após 2 tentativas: {e}")
            page.wait_for_timeout(2_000)
```

> **Nota:** a separação v3/v4 é temporária. No futuro, a navegação será inteligente (ver `genesis/services/subgrupo_service.py` como referência de abordagem).

#### Flow de Preenchimento (`preencher_*`)

Recebe dicts do `contexto_cliente`. O **último** flow de preenchimento de uma sequência de cadastro faz o submit e chama `esperar_sucesso_ou_erro`. Usa `escopo(page)` para obter o contexto correto (frame ou page) antes de interagir com elementos.

```python
from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo


def preencher_*(page: Page, almoxarifado: dict[str, str], material: dict[str, str], quantidade: str = "1") -> None:
    logger.info("Iniciou preenchimento de *.")

    nome_completo_material = f"{material['nome']} {material['complemento']}"
    ctx = escopo(page)

    preencher_campo(ctx, "input[name='almoxarifadoDestino']", almoxarifado["sigla"])
    preencher_campo(ctx, "input[name='cdBemServico-1-3']", nome_completo_material)

    campo_qtd = ctx.locator("input[name='qtRequisicao-2-5']")
    campo_qtd.click()
    campo_qtd.fill(quantidade)

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou preenchimento de *.")
```

> Quando a página tem muitos campos, divida em múltiplos flows: `preencher_dados_gerais`, `preencher_documentos`, etc. Um flow por responsabilidade lógica.

#### Flow de Consulta (`consultar_*`)

Retorna `None` — apenas aplica os filtros e submete a busca. **Não seleciona o resultado.**

```python
from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def consultar_*(page: Page, almoxarifado: dict[str, str], material: dict[str, str]) -> None:
    logger.info("Iniciou consulta de *.")

    ctx = escopo(page)
    nome_completo_material = f"{material['nome']} {material['complemento']}"

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    preencher_campo(ctx, "input[name='model-0']", almoxarifado["sigla"])
    preencher_campo(ctx, "input[name='model-8']", nome_completo_material)
    preencher_campo(ctx, "input[name='model-10']", "ATENDER")

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de *.")
```

#### Flow de Seleção (`selecionar_*`)

Retorna `bool`. Na maioria dos casos, delega para `selecionar_movimentacao` de `flows/shared/`.

```python
from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao


def selecionar_*(page: Page, almoxarifado: dict[str, str]) -> bool:
    logger.info("Iniciou seleção de *.")

    ctx = escopo(page)
    encontrou = selecionar_movimentacao(ctx, almoxarifado["nome"])

    if not encontrou:
        logger.info("Nenhum registro encontrado para '{}'.", almoxarifado["nome"])
        return False

    logger.info("Finalizou seleção de *.")
    return True
```

#### Flow de Alteração (`alterar_*`)

Retorna `bool` se a alteração pode ser impossível em determinadas condições; `None` quando sempre é possível executar.

```python
from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def alterar_*(page: Page) -> bool:
    logger.info("Iniciou alteração de *.")

    ctx = escopo(page)
    campo = ctx.locator("input[name='campo']")

    if campo.is_disabled():
        logger.info("Campo desabilitado. Não é possível fazer alteração.")
        return False

    campo.fill("novo_valor")
    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou alteração de *.")
    return True
```

### 3.4 Logs

- Toda função começa com `logger.info("Iniciou ...")` e termina com `logger.info("Finalizou ...")`.
- O nome da operação usa **capitalização de título**: `"Iniciou teste de Cadastro de Transferência entre Almoxarifados."`.
- Quando um teste é pulado: `logger.warning("Pulando teste.")` **antes** do `pytest.skip()`.
- Funções auxiliares internas (`_v3`, `_v4`) não têm logs próprios — os logs ficam na função pública.
- `logger.warning` é para condições anômalas (dados ausentes, campo desabilitado, skip). `logger.info` é para fluxo normal.

### 3.5 Tratamento de dados ausentes (skip)

Quando um flow retorna `False`, o teste deve emitir warning e chamar `pytest.skip()`:

```python
existe = selecionar_*(page, almoxarifado)
if not existe:
    logger.warning("Pulando teste.")
    pytest.skip()
```

**Exceção:** módulos auxiliares sem contexto de dados (tabelas de configuração) podem usar `return` em vez de `pytest.skip()` quando a ausência do dado é esperada e não representa falha de ambiente.

### 3.6 Impressão de relatório

Deve ser chamada após toda operação de cadastro que gere um documento imprimível:

```python
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio

imprimir_relatorio(page)
```

O flow trata internamente o formato (PDF/HTML), valida o conteúdo e registra a evidência. Não é necessário tratar o retorno no teste.

### 3.7 Flows compartilhados essenciais

| Flow | Assinatura | Uso |
| --- | --- | --- |
| `login_flow` | `login(page, dados_cliente)` | Sempre o primeiro call do teste |
| `logout_flow` | `logout(page)` | Sempre o penúltimo call (antes do log de finalização) |
| `imprimir_relatorio_flow` | `imprimir_relatorio(page)` | Após cadastro bem-sucedido |
| `excluir_movimento_flow` | `excluir_movimento(page, esperar_sucesso=True)` | Exclusão em almoxarifado |
| `excluir_movimento_flow` | `excluir_movimento(page)` | Exclusão em patrimônio |
| `selecionar_movimentacao_flow` | `selecionar_movimentacao(ctx, texto, table_locator, posicao)` | Seleção genérica de linha |

`selecionar_movimentacao` aceita `Page` ou `Frame` como primeiro argumento e retorna `bool`.

### 3.8 Seletores recorrentes

| Ação | Seletor |
| --- | --- |
| Abrir painel de filtros | `button[name='submitSearch']` (primeiro clique) |
| Submeter busca | `button[name='submitSearch']` (segundo clique) |
| Confirmar / salvar formulário | `button[name='submitFinish']` |
| Selecionar linha do resultado | `button[name='submitUse']` |
| Excluir registro | `page.get_by_role("button", name="Excluir")` |

### 3.9 O que não fazer

| Proibido | Alternativa |
| --- | --- |
| `time.sleep()` | `aguardar_ajax_global`, `esperar_sucesso_ou_erro` de `utils/waits.py` |
| Dados hardcoded nos testes | `contexto_cliente.*` |
| Lógica de UI dentro do teste | Mover para um flow |
| Flow que combina consulta + seleção | Dois flows separados: `consultar_*` e `selecionar_*` |
| Múltiplas operações de negócio em um único flow | Um flow, uma responsabilidade |
| Função principal + função interna sem motivo real | Uma função por flow; funções auxiliares (`_v3`, `_v4`) só para bifurcação de versão |
| `pytest.skip()` em testes de cadastro | Cadastros não dependem de dados preexistentes — falha é bug |

---

## 4. Catálogo da GUI

Todo teste novo deve ser registrado em `gui/catalog/modules_catalog.py`. Inserir logo abaixo da entrada de consulta correspondente:

```python
{
    "name": "Cadastro de Transferência entre Almoxarifados",
    "path": "tests/almoxarifado/movimentacao_externa/test_cadastro_transferencia_entre_almoxarifados.py"
},
```

### Visibilidade por cliente

Dois campos opcionais controlam para quais clientes o teste aparece na GUI:

**`clients`** — teste visível **somente** para os clientes listados:

```python
{
    "name": "Fechar Mês",
    "path": "tests/patrimonio/financeiro/test_fechar_mes_pcdf.py",
    "clients": ["pcdf", "pcdfv4"]
},
```

**`exclude_clients`** — teste visível para todos os clientes **exceto** os listados:

```python
{
    "name": "Entrada Compra",
    "path": "tests/almoxarifado/movimentacao_interna/test_entrada_simples.py",
    "exclude_clients": ["seadpb"]
},
```

Use `clients` quando o teste é específico de um ou poucos clientes (ex.: fluxo exclusivo de um órgão). Use `exclude_clients` quando o teste é geral mas um ou poucos clientes têm restrição conhecida. Não use os dois campos ao mesmo tempo.

> Documentação completa da GUI (arquitetura, execução de testes/Genesis via subprocess, componentes): [`GUIA_GUI.md`](GUIA_GUI.md).

---

## 5. Evidências e logs

### Evidências

A coleta é gerenciada por `utils/evidencia.py` e integrada ao ciclo do Pytest em `conftest.py`:

1. Início de sessão: cria área temporária de evidência.
2. Durante os testes: screenshots e PDFs são registrados sob demanda.
3. Em falha de teste: a evidência é finalizada e movida para `evidencia/<YYYY-MM-DD_HH-MM-SS>/`.
4. Em teardown: finalização é reforçada para fechamento consistente.

### Logs

Logs de execução por teste são gerenciados por `utils/logging_manager.py`:

- Pasta diária: `logs/<YYYY-MM-DD>/`
- Arquivo por teste (nodeid sanitizado): `logs/<data>/<arquivo>.txt`

### Comportamento em falha

Quando um teste falha na fase `call`:

- Screenshot é capturada automaticamente (`falha-<nodeid>.png`)
- Evidência da execução é consolidada
- O log do teste é mantido na pasta de logs diária

### Traces do Playwright

Traces são salvos em `trace/` e podem ser abertos para inspeção detalhada:

```bash
playwright show-trace trace/<nome-do-trace>.zip
```

Ou pelo [site oficial](https://trace.playwright.dev/)

---

## 6. Particularidades do ASI

### Restrições de Perfil — Corporativo

Por mais que os usuários da LinkData possuam perfil de administrador, ainda é possível encontrar restrições que impedem alguns testes. Quando uma entidade não aparecer ou não estiver disponível, verifique as restrições de perfil em `Corporativo → Segurança → Perfil`.

Restrições também podem ser encontradas em `Corporativo → Segurança → Usuário`. Pesquise o usuário, clique em **"AÇÕES"** e acesse a aba **"AUTORIZAÇÃO"**.

Para encontrar todas as restrições de um módulo:

> Corporativo → Segurança → Perfil → Consultar perfil desejado → Imprimir → Relatório Relação dos Perfis → CTRL+F → Pesquisar por "Restringir"

### Unidade de Localização de Estoque — Patrimônio

A Unidade de Localização de Estoque (UL) organiza onde os bens estão armazenados. Sem ela, é **impossível realizar a entrada de bens**. Para fazer açõe como baixa e transferência temporária, é necessário tirar o bem da UL de estoque fazendo uma transferência interna. Só então ele fica disponível para as demais operações.

### Endereçamento de Material — Almoxarifado

Só é possível realizar a entrada de um material se houver endereço definido para ele. Caminho: `Almoxarifado → Auxiliares → Endereçamento`. Para associar um endereço a um material, primeiramente é necessário que o endereço já esteja criado.

### Intervalo de Número Patrimonial — Patrimônio

Precisa ser configurado antes de cadastrar novos bens em uma UG. Caminho: `Patrimônio → Auxiliares → Intervalo de Nº Patrimoniais`.

### Baixa — Patrimônio

A baixa de um bem só pode ser efetuada se ele estiver **fora da Unidade de Localização de Estoque**. Para isso, realize uma transferência interna do bem para qualquer UL que não seja de estoque.

Para realizar uma baixa sem avisos, a situação física do bem deve ser **diferente de "NOVO"**. Caminho para modificar: `Patrimônio → Modificação → Situação Física`.

### Estorno de Baixa — Patrimônio

O estorno só pode ser realizado se a situação da baixa for **"AUTORIZADA"**. É possível escolher a situação no cadastro ou editá-la pela consulta de baixa.

### Recebimento de Transferência Interna — Patrimônio

Uma transferência interna só pode ser recebida se, no momento do cadastro, a opção **"Exige Assinatura Eletrônica"** tiver sido marcada. Isso também se aplica a Detentor do Bem — Recebimento.

### Entrada de Materiais — SEADPB

Não é possível realizar entradas do tipo **"COMPRA"** devido à integração com o sistema financeiro da SEADPB. Usar o tipo **"EXTRA-ORÇAMENTÁRIA"**.

### Fechamento de Mês — PCDF (v3 e v4)

O fechamento de mês é feito em `Patrimônio → Financeiro → Resumo Mensal de Bens (RMB)`, não pelo fluxo padrão (`Ano/Mês Referência UG`).

Instruções:

1. Selecione a UG.
2. Digite o ano/mês nos dois campos de data (mesmo valor em ambos).
3. Marque "Fechar mês".
4. Confirme.

Se o ano/mês for **maior** que o mostrado na tabela → fecha o mês. Se for **menor** → abre o mês. Se for **igual** → nada acontece.

### Relatório de Empenho

| Versão | Caminho |
| --- | --- |
| v3 | `Almoxarifado → Gestão de Compras → Relatórios de Empenho` |
| v4 | `Almoxarifado → Relatórios → Empenho` |

---

## 7. Suporte a múltiplas versões do GRP (v3/v4)

### Regra fundamental

Os testes **não sabem** a versão do GRP. Apenas os flows sabem. Os testes chamam flows por nome; os flows usam `get_versao()` e `escopo(page)` para adaptar o comportamento internamente.

### Quando usar `escopo(page)` vs `get_versao()`

| Tipo de diferença | Padrão a usar | Onde aparece |
| --- | --- | --- |
| v4 usa iFrame, v3 usa DOM direto | `ctx = escopo(page)` | Preenchimento, consulta, seleção |
| Menu/navegação mudou estruturalmente | `if get_versao() >= 4: _v4() else: _v3()` | Flows de `navegar_para_*` |
| Diferença mínima (< 5 linhas) | `if/else` pontual | Logout, confirmações |

```python
from utils.versao import escopo, get_versao

# Padrão 1: frame vs page (usar escopo)
def preencher_dados(page: Page, almoxarifado: dict) -> None:
    ctx = escopo(page)   # page na v3, frame na v4
    ctx.locator("input[name='almoxarifado']").fill(almoxarifado["sigla"])
    aguardar_ajax_global(page)   # sempre page — nunca ctx

# Padrão 2: lógica genuinamente diferente (usar get_versao)
def acessar_entrada_materiais(page: Page) -> None:
    if get_versao() >= 4:
        _v4(page)
    else:
        _v3(page)
```

> Este mesmo padrão (`escopo`/`get_versao`) é o padrão-alvo da refatoração do **Genesis** (motor de provisão de dados, executado antes dos testes). Veja [`GUIA_GENESIS.md`](GUIA_GENESIS.md) para a arquitetura completa do Genesis e o estado atual dessa migração.

---

## 8. Histórico e Estado Atual dos Testes por Cliente

A infraestrutura de testes intercepta a execução do Pytest para manter um registro persistente do estado mais recente dos testes executados por cliente.

### Funcionamento Interno
- **Hook Pytest:** Intercepta o término de cada teste (`pytest_runtest_logreport`) e extrai o módulo e o resultado (`pass`, `fail` ou `skip`).
- **Persistência:** Salva os dados em `historico_testes/estado_atual/<cliente>.json`.
- **Concorrência e Integridade:** Utiliza trava com `FileLock` (`.lock`) e escrita atômica via arquivo temporário (`.json.tmp`) com `os.replace` para evitar *race conditions* e corrupção de arquivos.

### Estrutura do JSON Gerado
```json
{
  "tests/modulo/sub_modulo/test_exemplo.py::test_funcao": {
    "data": "2026-09-08T09:00:00-03:00",
    "resultado": "pass",
    "modulo": "modulo"
  }
}
