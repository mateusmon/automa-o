# Como produzir casos de teste?

Boa pergunta. Esse é um problema clássico de escalabilidade em frameworks de automação — como ir de testes unitários de operações para casos de teste que exercitam fluxos de negócio completos.

Deixa eu te mostrar como penso que isso se encaixa bem na arquitetura que você já tem.

## O problema central

Você tem dois tipos de teste fundamentalmente diferentes:

**Testes unitários de operação** (o que você tem hoje): "O sistema consegue fazer uma entrada de material?"

**Casos de teste de negócio** (o que você quer): "O fluxo completo de requisição funciona — desde o cadastro até o atendimento e recebimento?"

Eles têm propósitos diferentes, então faz sentido separar.

---

## Estrutura sugerida

```text
tests/
├── almoxarifado/              # testes unitários (o que você tem hoje)
│   ├── movimentacao_interna/
│   │   ├── test_entrada_simples.py
│   │   └── test_cadastro_requisicao.py
│   └── consulta/
│       └── test_consulta_simples.py
│
└── casos/                     # nova pasta para casos de negócio
    └── almoxarifado/
        └── test_ciclo_requisicao_completo.py
```

A separação é importante porque os casos de teste têm ciclo de vida, ordem e dependências que os unitários não têm.

---

## Como reutilizar flows nos casos de teste

Você **não precisa mudar nada** nos flows existentes. Eles já são funções independentes — é só importar e encadear.

```python
# tests/casos/almoxarifado/test_ciclo_requisicao_completo.py

from loguru import logger

from flows.shared.login_flow import login
from flows.almoxarifado.movimentacao_interna.cadastro_requisicao.navegar_para_cadastro_requisicao_flow import acessar_cadastro_requisicao
from flows.almoxarifado.movimentacao_interna.cadastro_requisicao.preencher_demais_campos_flow import preencher_demais_campos
from flows.almoxarifado.movimentacao_interna.cadastro_requisicao.garantir_ur_valida_flow import garantir_ur_valida
from flows.almoxarifado.movimentacao_interna.atendimento_requisicao.navegar_para_atendimento_flow import acessar_atendimento_requisicao
from flows.almoxarifado.movimentacao_interna.atendimento_requisicao.atender_requisicao_flow import atender_requisicao
from flows.almoxarifado.movimentacao_interna.recebimento_requisicao.navegar_para_recebimento_flow import acessar_recebimento_requisicao
from flows.almoxarifado.movimentacao_interna.recebimento_requisicao.receber_requisicao_flow import receber_requisicao
from flows.shared.garantir_sucesso_movimentacao_flow import garantir_sucesso_movimentacao


def test_ciclo_requisicao_completo(page, contexto_cliente):
    dados_cliente = contexto_cliente.dados_cliente()
    ur = contexto_cliente.ur_padrao()
    almoxarifado = contexto_cliente.almoxarifado_padrao()
    material = contexto_cliente.material_padrao()

    logger.info("=== INÍCIO DE CASO DE TESTE: Ciclo Completo de Requisição ===")

    login(page, dados_cliente)

    # Passo 1 — Cadastro
    logger.info("--- Passo 1: Cadastrar requisição ---")
    acessar_cadastro_requisicao(page)
    garantir_ur_valida(page, ur)
    preencher_demais_campos(page, almoxarifado, material)
    assert garantir_sucesso_movimentacao(page), "Falha ao cadastrar requisição."

    # Passo 2 — Atendimento
    logger.info("--- Passo 2: Atender requisição ---")
    acessar_atendimento_requisicao(page)
    atender_requisicao(page, ur)
    assert garantir_sucesso_movimentacao(page), "Falha ao atender requisição."

    # Passo 3 — Recebimento
    logger.info("--- Passo 3: Receber requisição ---")
    acessar_recebimento_requisicao(page)
    receber_requisicao(page)
    assert garantir_sucesso_movimentacao(page), "Falha ao receber requisição."

    logger.info("=== FIM DE CASO DE TESTE: Ciclo Completo de Requisição ===")
```

O caso de teste é só uma sequência mais longa de flows. A lógica continua nos flows, o teste só orquestra.

---

## E quando você precisar de um "sub-fluxo" compartilhado?

Se dois casos de teste diferentes precisam, por exemplo, "ter uma requisição cadastrada" antes de começar, você cria um flow de setup:

```text
flows/
└── casos/
    └── setup_requisicao_cadastrada_flow.py
```

```python
# flows/casos/setup_requisicao_cadastrada_flow.py
# Cria uma requisição e retorna os dados necessários para o próximo passo

def setup_requisicao_cadastrada(page, ur, almoxarifado, material):
    logger.info("Setup: Criando requisição para o caso de teste.")
    acessar_cadastro_requisicao(page)
    garantir_ur_valida(page, ur)
    preencher_demais_campos(page, almoxarifado, material)
    assert garantir_sucesso_movimentacao(page)
    logger.info("Setup: Requisição criada com sucesso.")
```

Assim o caso de teste fica limpo:

```python
setup_requisicao_cadastrada(page, ur, almoxarifado, material)
atender_requisicao(page, ur)
receber_requisicao(page)
```

---

## Catálogo

Adicione uma seção de casos no catálogo, separada visualmente na GUI:

```python
MODULES = {
    # ... módulos existentes ...

    "Casos de Teste": {
        "meta": {},
        "sections": {
            "Almoxarifado": [
                {
                    "name": "Ciclo Completo de Requisição",
                    "path": "tests/casos/almoxarifado/test_ciclo_requisicao_completo.py"
                },
            ]
        }
    }
}
```

---

## Resumo das decisões

**Pasta `tests/casos/`** — separa casos de negócio dos testes unitários. Fica claro o que é "testa uma operação" vs "testa um fluxo de negócio".

**Reutilize flows diretamente** — não crie wrappers desnecessários. Se o flow já existe, importe-o. A granularidade dos seus flows já está boa para isso.

**Crie flows de setup em `flows/casos/`** apenas quando dois ou mais casos precisam do mesmo estado inicial — aí vale extrair.

**Não tente "reaproveitar testes"** (chamar `test_X` dentro de `test_Y`). Reuse os flows, não os testes. Os testes são a camada de orquestração, não de lógica.

## Organização dos casos de teste

Separar por módulo faz muito sentido. A estrutura ficaria assim:

```text
tests/casos/
├── almoxarifado/
│   ├── test_ciclo_requisicao_completo.py
│   └── test_ciclo_compra_completo.py
├── patrimonio/
│   └── test_ciclo_entrada_bem.py
└── ...
```

E os flows de setup correspondentes:

```text
flows/casos/
├── almoxarifado/
│   └── setup_requisicao_cadastrada_flow.py
└── patrimonio/
    └── ...
```

A separação por módulo dentro de `casos/` tem duas vantagens: você consegue rodar só os casos de um módulo específico pelo terminal (`pytest tests/casos/almoxarifado/`), e a estrutura espelha a dos testes unitários, então fica intuitivo para quem já conhece o projeto.

---

## GUI — "Casos de Teste" como módulo de primeiro nível

A ideia de colocar casos de teste como um módulo de primeiro nível na GUI, com submódulos internos (Almoxarifado, Patrimônio...), é boa e encaixa perfeitamente na estrutura do `MODULES` que você já tem. Ficaria assim no catálogo:

```python
MODULES = {
    "Casos de Teste": {
        "meta": {},
        "sections": {
            "Almoxarifado": [...],
            "Patrimônio": [...],
        }
    },
    "Almoxarifado": { ... },  # testes unitários
    "Patrimônio": { ... },
    ...
}
```

Como o Python preserva a ordem de inserção em dicionários desde a 3.7, colocar "Casos de Teste" primeiro no `MODULES` já garante que ele apareça primeiro na GUI — sem nenhuma mudança na lógica de renderização.

---

## GUI — Layout responsivo em colunas

Aqui vale pensar um pouco mais antes de codar, porque a decisão afeta como o `ModulesBuilder` renderiza os módulos.

Hoje você tem tudo em coluna única. O que você quer é essencialmente um **grid fluido de seções**, onde cada "card" de seção (ex: "Movimentação Interna", "Gestão de Compras") ocupa uma célula do grid, e o número de colunas se ajusta à largura da janela.

As abordagens possíveis no Tkinter são duas:

**1. Grid fixo com `columnconfigure`** — você define 3 ou 4 colunas no frame pai e distribui as seções entre elas. Simples, mas não reage a redimensionamento automaticamente — você teria que ouvir o evento `<Configure>` da janela e redistribuir manualmente.

**2. Reflow por evento** — você ouve `<Configure>` no frame pai, calcula quantas colunas cabem com base na largura atual (ex: `largura // 300`), e redistribui os widgets. Isso dá o comportamento verdadeiramente responsivo que você descreveu.

A abordagem 2 é a correta para o que você quer. O ponto de atenção é que o `ModulesBuilder` precisaria expor uma lista de "cards de seção" prontos, e uma função de layout separada faria o reflow — em vez de o builder já gravar as posições fixas no `__init__`.

Uma separação limpa seria:

- `ModulesBuilder` cria os widgets de cada seção mas não os posiciona
- Uma função `reflow(largura)` posiciona usando `grid()` com o número de colunas calculado
- Essa função é chamada na inicialização e no evento `<Configure>`

---

## Resumo do planejamento

**Curto prazo (estrutural, sem impacto na GUI):**

- Criar `tests/casos/{modulo}/` e `flows/casos/{modulo}/`
- Adicionar "Casos de Teste" no início do `MODULES`

**Médio prazo (GUI):**

- Refatorar `ModulesBuilder` para separar criação de widgets do posicionamento
- Implementar `reflow()` com escuta no evento `<Configure>`

Essa ordem faz sentido porque a estrutura de pastas e catálogo não depende da GUI — você já pode começar a escrever casos de teste enquanto o layout ainda é coluna única.
