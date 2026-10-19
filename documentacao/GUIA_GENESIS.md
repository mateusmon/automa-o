# Guia do Genesis

O Genesis é o motor de provisão de dados do projeto. Ele roda **antes** da suíte de testes para garantir que o ambiente (cliente + ambiente) tenha todos os dados-base necessários (UF, cidade, UG, usuários, almoxarifados, materiais, bens etc.) — de forma **idempotente**: pode ser executado quantas vezes for preciso, criando apenas o que ainda não existe.

> Este documento assume que o leitor já conhece os conceitos gerais do projeto descritos em [`GUIA_TESTES.md`](GUIA_TESTES.md) (arquitetura flow/teste, `escopo`/`get_versao`, blueprints YAML). O Genesis reaproveita várias dessas ideias, mas tem sua própria estrutura de pastas e camadas.

## 1. Visão geral da arquitetura

```text
genesis/
├── blueprint/        # YAMLs de dados (mesmo conceito do genesis/blueprint usado pelos testes)
├── browser/          # Ciclo de vida do browser Playwright (BrowserManager)
├── config/           # Leitura de configs.yaml / configs.local.yaml (ConfigService)
├── core_logging/      # Configuração do Loguru
├── engine/            # Orquestração central (ExecutionContext, ProvisionEngine)
├── flows/             # Flows de provisão — funções garantir_*
├── routines/          # Rotinas de alto nível (sequência de flows por persona de usuário)
├── runner/            # Entry point (GenesisRunner)
├── services/          # Checagem de existência e criação de entidades
├── utils/             # versao_gen.py, trace.py, analizador.py (utilitários próprios do Genesis)
├── trace/             # Traces gerados em runtime (evidência de falha)
└── main.py            # Ponto de entrada chamado pela GUI
```

| Camada | Responsabilidade |
| --- | --- |
| `runner/genesis_runner.py` | Orquestra o ciclo de vida completo: carrega config, blueprint, sobe browser, executa o `ProvisionEngine`, trata sucesso/falha. Não contém lógica de domínio. |
| `engine/provision_engine.py` | Executa as `routines` em sequência, controlando limites de sessão (login/logout, reset de contexto do browser entre personas). |
| `engine/execution_step.py` | Executa cada flow/etapa dentro de uma sessão de trace isolada. |
| `engine/execution_context.py` | Dataclass imutável que carrega `browser_manager`, `runtime_config` e `blueprint` para todas as camadas abaixo. |
| `routines/*.py` | Sequência ordenada de flows `garantir_*` para uma persona de usuário (ex.: usuário "link", usuário "teste"). |
| `flows/*.py` (ou `flows/<entidade>/dispatcher.py`) | Um flow por entidade de dado. Lê a seção correspondente do blueprint, decide se precisa criar, e delega para o `service`. |
| `services/*.py` (ou `services/v3/`, `services/v4/`) | Implementam a checagem `*_existe()` e a criação (`_criar_*()`) via interação real com a UI do ASI. |

## 2. Como o Genesis é executado

```bash
python genesis/genesis_runner.py
```

Também disponível na GUI, pelo botão **"Preparar Ambiente"** (`gui/core/genesis_runner.py` sobe `genesis/main.py` como subprocesso e transmite os logs para o painel da GUI).

Fluxo de execução do `runner/genesis_runner.py`:

1. Configura o logger (Loguru).
2. Prepara o diretório e a retenção dos traces (`utils/trace.py`).
3. Carrega `runtime_config` via `ConfigService` (cliente ativo, ambiente, versão, URL, usuários, caminho do blueprint).
4. Carrega o blueprint YAML correspondente.
5. Define a versão global do GRP via `set_versao(runtime_config["versao"])`.
6. Sobe o browser via `BrowserManager`.
7. Monta o `ExecutionContext(browser_manager, runtime_config, blueprint)`.
8. Executa `ProvisionEngine(context).execute()`.
9. Em caso de sucesso: encerra com código 0 e popup de sucesso.
10. Cada flow, login e logout abre seu próprio trace; em sucesso ele é descartado e, em falha, é salvo com o nome da etapa.
11. Em caso de falha: mostra popup de erro e encerra com código 1.
12. Sempre encerra o browser ao final (`_safe_shutdown`).

## 3. Ordem de execução (routines)

O `ProvisionEngine` executa as rotinas em sequência, com **reset de contexto do browser** entre elas (login/logout completos, sessão limpa):

**Rotina 1 — `routines/link_user.py`** (login como usuário "link"):

```text
garantir_uf → garantir_cidade → garantir_ug → garantir_funcionarios → garantir_funcao
→ garantir_centro_custo → garantir_ua → garantir_associacao_funcionarios_ua
→ garantir_instalacao → garantir_enderecos → garantir_urs → garantir_perfis
→ garantir_usuarios → remover_restricoes_perfis
```

**Rotina 2 — `routines/teste_user.py`** (login como usuário "teste", sessão nova):

```text
garantir_almoxarifados → garantir_fornecedores → garantir_um → garantir_subgrupos
→ garantir_materiais → garantir_endereco_material → garantir_enderecamentos
→ garantir_uls → garantir_ul_estoque → garantir_catalogos → garantir_bens
→ garantir_intervalo_patrimonial
```

Essa ordem existe porque há dependências reais entre os dados (ex.: não dá para garantir uma UA sem a UG já existir).

## 4. Padrão atual da refatoração: escopo + get_versao

O Genesis está em processo de migração do padrão antigo (um arquivo por versão) para o **mesmo padrão usado pelos flows da suíte de testes**: um único arquivo por flow/service, usando `escopo(page)` e `get_versao()` para tratar as diferenças entre v3 e v4 internamente.

> O Genesis tem sua própria cópia desse mecanismo em `genesis/utils/versao_gen.py` (espelha `utils/versao.py`, usado pela suíte de testes):

```python
_versao: int = 3

def set_versao(v: int) -> None:
    global _versao
    _versao = int(v)

def get_versao() -> int:
    return _versao

def escopo(page):
    """
    Retorna o contexto de interação com a DOM para a versão ativa.

    - v4+: retorna o frame de conteúdo (a UI é renderizada dentro de um iframe)
    - v3 e anteriores: retorna a própria page

    Uso nos flows/services:
        ctx = escopo(page)
        ctx.locator("...").click()
        aguardar_ajax_global(page)  # page continua acessível diretamente
    """
    if _versao >= 4:
        from utils.espera import obter_frame_conteudo
        return obter_frame_conteudo(page)
    return page
```

### Padrão-alvo (exemplo real): `services/subgrupo_service.py`

Hoje considerado o exemplo de referência para qualquer refatoração de service/flow no Genesis:

```python
from loguru import logger
from playwright.sync_api import Page, expect

from utils.espera import aguardar_ajax_global, clicar_home_com_retry, select_tipo, preencher_campo, clicar_menu_com_retry
from utils.versao_gen import escopo, get_versao


def subgrupo_existe(page: Page, nome_subgrupo: str) -> bool:
    """
    Retorna True se o subgrupo existe.
    Lança exceção se houver duplicatas.
    """
    heading = page.get_by_role("heading", name="Material - Supply")
    if not heading.is_visible():
        _navegar_para_subgrupo(page)

    ctx = escopo(page)  # contexto único — page (v3) ou frame (v4)

    ctx.locator("button[name='lookup-grupoDsExemplo']").click()
    aguardar_ajax_global(page)

    ctx.get_by_text("Procurar por:").wait_for(state="visible", timeout=30_000)
    ctx.locator("select[name='tpFil']").wait_for(state="visible")

    select_tipo(ctx, "tpFil", "SUBGRUPO")
    preencher_campo(ctx, "input[name='filtro']", nome_subgrupo)

    try:
        ctx.locator("img.x-tree-node-icon.icon-subgrupo-open").wait_for(state="visible", timeout=1_000)
        existe = True
    except Exception:
        existe = False

    ctx.locator("button[name='submitCancel']").click()
    aguardar_ajax_global(page)
    return existe


def _navegar_para_subgrupo(page):
    for tentativa in range(2):
        try:
            if get_versao() == 4:   # diferenças pontuais de navegação ficam isoladas aqui
                clicar_home_com_retry(page)
                aguardar_ajax_global(page)
                page.get_by_text("Corporativo", exact=True).click()
                page.get_by_title("Abrir menu").locator("i").click()
                page.get_by_text("Material").click()
                page.get_by_text("Supply").click()
                aguardar_ajax_global(page)
                page.locator("i").nth(2).click()
                expect(page.get_by_role("heading", name="Material - Supply")).to_be_visible()
            else:
                clicar_menu_com_retry(page)
                aguardar_ajax_global(page)
                page.get_by_role("link", name="Corporativo").click()
                page.get_by_role("link", name="Material / Serviço").click()
                page.get_by_text("Supply").click()
                expect(page.get_by_role("heading", name="Supply")).to_be_visible()
            return
        except Exception as e:
            logger.warning("Navegação falhou. Tentando mais uma vez.")
            if tentativa == 1:
                raise RuntimeError(f"Falha ao concluir navegação após 2 tentativas: {e}")
            page.wait_for_timeout(2_000)
```

**Regras do padrão-alvo:**

- Um único arquivo para v3 e v4 — nunca criar `_v3.py` / `_v4.py` ou pastas `v3/`/`v4/` em código novo.
- `escopo(page)` é usado para qualquer interação com elementos da página (locators, clicks, fills) — ele decide internamente se a interação é direta na `page` (v3) ou via `frame` de conteúdo (v4).
- `get_versao()` só é consultado quando a própria navegação ou fluxo de tela muda estruturalmente entre versões (ex.: menus diferentes) — não para diferenças triviais de seletor.
- `aguardar_ajax_global(page)` continua recebendo `page` diretamente, nunca o `ctx`/`frame`.

### Padrão antigo (ainda presente em boa parte do código — a ser eliminado)

A maioria dos flows e services hoje ainda segue o padrão antigo: um **dispatcher** que decide em runtime qual implementação (`v3.py` ou `v4.py`) chamar.

```text
flows/garantir_ug/
├── dispatcher.py
├── v3.py
└── v4.py
```

`dispatcher.py`:

```python
from engine.execution_context import ExecutionContext
from flows.garantir_ug import v3
from flows.garantir_ug import v4


def garantir_ug(context: ExecutionContext) -> None:
    """
    Dispatcher de versão para o flow garantir_ug.
    Lê a versão do cliente em runtime_config e roteia para a implementação correta.
    """
    version = context.runtime_config.get("versao")

    if version == 3:
        v3.garantir_ug(context)
        return

    if version == 4:
        v4.garantir_ug(context)
        return

    raise RuntimeError(f"Versão de cliente não suportada para o flow garantir_ug: {version}")
```

As rotinas sempre importam o `dispatcher`, nunca `v3`/`v4` diretamente:

```python
from flows.garantir_ug.dispatcher import garantir_ug
```

O mesmo padrão se repete em `services/v3/*.py` e `services/v4/*.py` — implementações completas e paralelas da mesma entidade, uma por versão, sem nenhum código compartilhado.

**Esse padrão está sendo descontinuado.** Ele existe hoje em: `garantir_almoxarifados`, `garantir_associacao_funcionarios_ua`, `garantir_bens`, `garantir_catalogos`, `garantir_enderecamentos`, `garantir_endereco_material`, `garantir_enderecos`, `garantir_fornecedores`, `garantir_funcao`, `garantir_funcionarios`, `garantir_instalacao`, `garantir_materiais`, `garantir_perfis`, `garantir_ua`, `garantir_um`, `garantir_usuarios`, `garantir_urs`, `garantir_ul_estoque`, `garantir_classificacao_material_consumo` (este último ainda sem `v4.py`), além de todos os `services/v3/*.py` e `services/v4/*.py`.

### Já migrados para o padrão-alvo

`garantir_uf_flow.py`, `garantir_cidade_flow.py`, `garantir_centro_custo_flow.py`, `garantir_grupos_subgrupos_flow.py`, `garantir_intervalo_patrimonial_flow.py`, `remover_restricoes_perfis_flow.py`, e os services `uf_service.py`, `cidade_service.py`, `centro_custo_service.py`, `subgrupo_service.py`, `intervalo_patrimonial_service.py`.

### Como migrar um par v3/v4 para o padrão único

1. Ler as duas implementações (`v3.py` e `v4.py`) lado a lado e identificar o que é **igual** (seletores, lógica de negócio) e o que é **estrutural** (navegação, uso de `frame` vs `page`).
2. Criar um único arquivo (ex.: `services/ug_service.py`, eliminando a pasta `services/v3/`/`services/v4/` ou o par `flows/garantir_ug/v3.py`+`v4.py`).
3. Substituir qualquer interação direta de UI por `ctx = escopo(page)` seguido de `ctx.locator(...)`.
4. Isolar a navegação que difere estruturalmente entre versões em uma função privada com `if get_versao() == 4: ... else: ...` (ver `_navegar_para_subgrupo` acima).
5. Apagar o `dispatcher.py` e os arquivos antigos da pasta de versão; atualizar o import na rotina para apontar para o novo arquivo único.
6. Rodar o Genesis nos dois ambientes (um cliente v3, um cliente v4) para validar que o comportamento se manteve idêntico.

> **Nota**: Sempre que houver diferenças estruturais de código entre v3 e v4, prefira o padrão da v4, que é mais atualizado e feito com foco em velocidade e confiabilidade.

## 5. Convenções de nomenclatura

| Prefixo | Camada | Retorno | Significado |
| --- | --- | --- | --- |
| `garantir_*` | `flows/` | `None` | Garante que uma entidade exista — lê o blueprint, verifica existência, cria se necessário. |
| `*_existe` | `services/` | `bool` | Verifica se a entidade já existe na base. Lança exceção se encontrar duplicatas. |
| `_criar_*` | `services/` | `None` | Função privada — cria a entidade via UI. Assume que `*_existe()` já retornou `False`. |
| `_navegar_para_*` | `services/` | `None` | Função privada — navegação até a tela da entidade. |
| `remover_*` | `flows/` | `None` | Remove/desfaz uma configuração (ex.: `remover_restricoes_perfis`). |

## 6. Padrão de idempotência (obrigatório em todo flow `garantir_*`)

Todo flow `garantir_*` segue exatamente esta estrutura:

```python
def garantir_uf(context: ExecutionContext) -> None:
    page = context.browser_manager.page
    blueprint = context.blueprint
    uf_data = blueprint.get("uf")

    if not uf_data:
        logger.info("Nenhuma UF definida no arquivo yaml. Ignorando fluxo.")
        return

    nome = uf_data["nome"]
    logger.info("Garantindo UF de nome '{}'", nome)

    if uf_existe(page, nome):
        logger.info("UF '{}' já existe. Nenhuma ação é necessária.", nome)
        return

    logger.info("UF '{}' não encontrada. Criando...", nome)
    _criar_uf(page, uf_data)

    if not uf_existe(page, nome):
        raise RuntimeError(f"Falha ao validar criação da UF '{nome}'.")

    logger.success("UF '{}' criada com sucesso.", nome)
```

Regras:

- Se a seção correspondente não existir no blueprint, o flow loga e retorna — nunca falha por dado ausente.
- Sempre checar existência **antes** de criar (idempotência: rodar o Genesis várias vezes não deve duplicar nada nem falhar).
- Sempre validar a criação checando a existência novamente depois.
- Falhar (`raise`) se a validação pós-criação falhar, ou se `*_existe()` encontrar duplicatas — nunca seguir em frente silenciosamente.

## 7. Blueprints (dados)

O Genesis lê os mesmos arquivos YAML usados como base de dados de teste, em `genesis/blueprint/<cliente>.yaml` (ou `blueprint.yaml` como modelo padrão). O caminho efetivo vem de `runtime_config["arquivo_dados"]`, definido em `configs/configs.yaml`.

```yaml
uf:
  nome: "D01 DISTRITO FEDERAL"
  pais: "BRASIL"
  sigla: "DF"

cidade:
  nome: "B01 BRASÍLIA"
  uf: "D01 DISTRITO FEDERAL"
  regiao: "CENTRO"

unidade_gestora:
  codigo: "778899"
  nome: "COORDENAÇÃO-GERAL DE TESTES E AUTOMAÇÃO DIGITAL"
  cidade: "B01 BRASÍLIA - DISTRITO FEDERAL"
  sigla: "CGTAD"
  admnistracao_direta: "sim"

funcionarios:
  - matricula: "76673826037"
    nome: "RAFAEL AUTOMAÇÃO DE CAMPOS"
    email: "RAFAEL.AUTOMACAO.CAMPOS@GMAIL.COM"
    sigla_ua: "SGRTA"
```

Cada flow lê apenas a seção que lhe interessa (`blueprint.get("uf")`, `blueprint.get("funcionarios")` etc.) — se a seção não existir, o flow simplesmente não provisiona aquele dado.

## 8. O que NÃO fazer

| Não fazer | Fazer no lugar |
| --- | --- |
| Criar novo flow/service com arquivos separados `v3.py`/`v4.py` ou pastas `v3/`/`v4/` | Usar `escopo(page)` + `get_versao()` em um único arquivo, seguindo `subgrupo_service.py` |
| Criar entidade sem checar `*_existe()` antes | Sempre checar existência antes de criar (idempotência) |
| Deixar de validar a criação após `_criar_*()` | Chamar `*_existe()` de novo após criar e lançar exceção se falhar |
| Importar `v3`/`v4` diretamente nas rotinas | Importar sempre o `dispatcher` (enquanto o padrão antigo ainda existir) |
| Hardcodar dados de cliente no flow/service | Ler sempre do `blueprint` via `ExecutionContext` |
| Usar `time.sleep()` | Usar os helpers de espera (`aguardar_ajax_global`, etc.) |
