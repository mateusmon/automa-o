# Sentinela — Planejamento Completo

## O que é

**Sentinela** é uma engine de validação da suite de automação ASI. Ela executa os
testes do projeto ASI Automação 2.0 em sequência controlada, para um ou mais
clientes, registrando resultados, logs e traces de cada execução. O objetivo é
descobrir quais testes falham em quais clientes *antes* que os testadores reclamem,
e produzir um relatório HTML consultável ao final.

Ela não substitui a engine principal de automação — ela a *audita*.

---

## Contexto do projeto

O ASI Automação 2.0 é organizado com a suite de automação como projeto principal,
e Genesis, GUI e Sentinela como subprojetos irmãos dentro do mesmo repositório.
A Sentinela vive em `sentinela/` na raiz do projeto.

```
ASI Automação 2.0/
├── tests/
├── flows/
├── genesis/
├── gui/
├── sentinela/        ← aqui
└── conftest.py
```

---

## Responsabilidades

| Responsabilidade | Descrição |
|---|---|
| **Validação** | Avisa sobre testes no catálogo que não estão na `ordem.yaml` |
| **Filtragem** | Lê o `modules_catalog` e determina quais testes estão disponíveis para cada cliente |
| **Ordenação** | Executa os testes na sequência definida manualmente em `ordem.yaml` |
| **Execução** | Roda cada teste via subprocess com pytest |
| **Retry** | Retenta em erros transientes de rede antes de registrar como falha |
| **Persistência** | Salva log e trace de cada execução, com TTL configurável |
| **Relatório** | Gera um HTML por cliente com panorama completo dos resultados |
| **Limpeza** | Remove runs antigos automaticamente conforme TTL na inicialização |

## O que está fora do escopo

- A Sentinela não corrige testes — só detecta e registra
- A Sentinela não adapta flows para clientes diferentes
- A Sentinela não tem interface gráfica
- A Sentinela não envia notificações
- A Sentinela não para quando um teste falha — continua até o fim da lista

---

## Estrutura de arquivos

```
sentinela/
├── sentinela.py            # Entrypoint CLI
├── ordem.yaml              # Jornadas lógicas ordenadas (aceita repetições)
├── config.yaml             # Configurações: tentativas, TTL
│
├── runner.py               # Orquestra a execução de todos os testes para um cliente
├── executor.py             # Executa um único teste via subprocess + pytest
├── reporter.py             # Gera o relatório HTML final
├── storage.py              # Persiste runs e aplica limpeza por TTL
├── catalog_reader.py       # Lê e interpreta o modules_catalog do projeto principal
│
└── reports/
    └── 2026-06-11_14h30_tcerj/
        ├── report.html
        ├── test_entrada_simples_1.log
        ├── test_entrada_simples_2.log      # Segunda ocorrência do mesmo teste
        └── test_alteracao_entrada_trace/   # Trace do Playwright (salvo em falha)
```

---

## Arquivo `ordem.yaml`

Lista de jornadas lógicas e ordenadas. Um mesmo teste pode aparecer mais de uma vez —
isso é intencional para fluxos que precisam recriar registros entre blocos de testes.
Uma jornada pode declarar pré-condições cujo path físico pertence a outro diretório. A
Sentinela seleciona a jornada pelo `--modulo` antes de filtrar silenciosamente os testes
indisponíveis para o cliente atual, sem registrá-los no relatório.

```yaml
modulos:
  - modulo: "tests/almoxarifado/movimentacao_interna"
    ordem:
      - path: "tests/almoxarifado/movimentacao_interna/test_entrada_simples.py"
      - path: "tests/almoxarifado/movimentacao_interna/test_consulta_entrada.py"
      - path: "tests/almoxarifado/movimentacao_interna/test_alteracao_entrada.py"
      - path: "tests/almoxarifado/movimentacao_interna/test_exclusao_ultima_entrada.py"

  - modulo: "tests/patrimonio/modificacao"
    ordem:
      # Pré-condição externa: cria o bem que os testes abaixo modificam.
      - path: "tests/patrimonio/movimentacao/test_entrada_patrimonio.py"
      - path: "tests/patrimonio/modificacao/test_detentor_bem_cadastro.py"
```

---

## Arquivo `config.yaml`

```yaml
tentativas: 3       # Número máximo de tentativas por teste em erro transiente
ttl_dias: 7         # Dias para manter os runs antes da limpeza automática
```

O ambiente é sempre `qas` — fixo no código. A opção `--ambiente` existe no CLI
para não fechar portas no longo prazo, mas não é um caso de uso esperado no dia a dia.

---

## Seleção de cliente

O cliente é sempre escolhido pelo usuário na hora de rodar, via `--cliente`.
A Sentinela usa esse valor para buscar as informações (URL, usuário, senha)
diretamente no `configs.yaml` do projeto principal.

O `configs.local.yaml` (não versionado) contém apenas o `cliente_ativo` usado
pela GUI e pela suite principal — a Sentinela o ignora completamente.

---

## Lógica de filtragem (`catalog_reader.py`)

O `modules_catalog` usa duas formas de restrição por cliente:

**1. Restrição no módulo inteiro** (`meta.clients`) — só os clientes listados têm acesso:
```python
"Compras": {
    "meta": { "clients": ["tse", "pcdf"] },
    ...
}
```

**2. Restrição por teste individual:**
```python
# Só este cliente tem o teste
{ "path": "...", "clients": ["pcdfv4"] }

# Todos os clientes exceto estes
{ "path": "...", "exclude_clients": ["seadpb"] }
```

A função `testes_disponiveis_para(cliente_id)` retorna um `set` de paths.
A Sentinela usa esse set para filtrar a `ordem.yaml` antes de executar qualquer coisa.
Testes filtrados por incompatibilidade de cliente não aparecem no relatório —
nem como skip, nem como qualquer outra categoria. São simplesmente ignorados.

### Validação de cobertura do catálogo

A Sentinela também faz o caminho inverso: itera todos os testes presentes no
`modules_catalog` e verifica quais **não estão** na `ordem.yaml`. Isso evita
que um teste adicionado ao catálogo (e visível na GUI) seja esquecido na Sentinela.

Esse aviso aparece sempre — tanto no `--dry-run` quanto no início de uma execução normal:

```
Atenção: 3 testes no catálogo não estão na ordem.yaml:
  - tests/almoxarifado/movimentacao_interna/test_exclusao_recebimento_devolucao.py
  - tests/patrimonio/auxiliares/test_consulta_conta_contabil.py
  - tests/corporativo/caracteristica_bem/test_definicao_bem.py
```

Testes comentados no catálogo são invisíveis para o Python e não são considerados.

---

## Lógica de execução (`executor.py`)

A Sentinela seleciona o cliente escrevendo temporariamente o `cliente_ativo` no
`configs.local.yaml` antes de cada execução via subprocess, e restaurando o valor
original ao final. Isso garante que o `conftest.py` da suite principal carregue
o cliente correto sem precisar de modificações.

Cada teste é executado como subprocess:

```bash
pytest tests/modulo/secao/test_nome.py -s --tb=long
```

O executor captura:
- Código de saída (`0` = passou, `1` = falhou, `5` = skip explícito do pytest)
- stdout + stderr completo (salvo como `.log`)
- Diretório de trace gerado pelo Playwright em falha (movido para `reports/`)

---

## Lógica de retry (`runner.py`)

O retry é simples e sem configuração externa. A regra é:

> Retenta se `TimeoutError` ou `net::ERR_` aparecer no traceback.
> Não retenta para nenhum outro tipo de erro.

**Erros transientes** (vale retry) — indicam problema de rede ou lentidão,
não relacionados ao código do teste:

| Erro | Causa provável |
|---|---|
| `TimeoutError` em `page.goto` ou `wait_for_load_state` | Site lento ou inacessível |
| `net::ERR_CONNECTION` | Falha de rede antes de chegar ao servidor |
| `net::ERR_NAME_NOT_RESOLVED` | DNS não resolveu o hostname — ambiente fora do ar |
| `net::ERR_INTERNET_DISCONNECTED` | Máquina perdeu conexão durante execução |
| `net::ERR_CONNECTION_REFUSED` | Servidor respondeu recusando — Jboss/Wildfly parado |
| `browser has been closed` | Crash do Chromium ou timeout de sessão |

**Erros definitivos** (não retenta) — indicam falha real no teste ou no sistema:

| Erro | Causa provável |
|---|---|
| `TimeoutError` em `locator.click`, `locator.fill`, `expect(...).to_be_visible` | Elemento não existe na página — estrutura mudou |
| `TimeoutError` em `page.wait_for_url` | Página redirecionou para lugar inesperado |
| `RuntimeError` | Lançado por `esperar_sucesso_ou_erro` quando o ASI retorna alerta vermelho — carrega a mensagem de negócio do sistema |
| `AssertionError` | Assert explícito falhou |

A distinção chave: `TimeoutError` de navegação é transiente. `TimeoutError` de
locator é definitivo — o Playwright chegou à página, mas o elemento não estava lá.

O intervalo entre tentativas é fixo: **10 segundos**.

```
Executou o teste
  └─ Passou?                    → registra ✅, fim
  └─ Skip explícito?            → registra ⚠️, fim
  └─ Falhou com erro transiente?
      └─ tentativas restantes?  → aguarda 10s, retenta
      └─ esgotou tentativas?    → registra ❌🔁 (retentou e falhou)
  └─ Falhou com erro definitivo → registra ❌ imediatamente, sem retry
  └─ Erro não classificado?     → trata como definitivo (não retenta)
```

Se retentou e passou em alguma tentativa: registra como ✅🔁.
O log de todas as tentativas é preservado, numerado.

---

## Relatório HTML (`reporter.py`)

### Cabeçalho

```
Sentinela — Run de 11/06/2026 14:30
Cliente: TCERJ  |  Ambiente: QAS
Duração total: 4m 32s

✅ 18 passaram   ❌ 3 falharam   ✅🔁 1 retentou e passou   ❌🔁 1 retentou e falhou   ⚠️ 1 skip explícito
```

### Tabela de resultados

| # | Teste | Status | Duração | Tentativas | Ações |
|---|---|---|---|---|---|
| 1 | Entrada Simples `[1/2]` | ✅ | 0.8s | 1/3 | — |
| 2 | Consultar Última Entrada | ✅ | 1.1s | 1/3 | — |
| 3 | Alterar Entrada | ❌ | 2.3s | 3/3 | [log] [trace] |
| 4 | Entrada Simples `[2/2]` | ✅🔁 | 3.1s | 2/3 | [log] |
| 5 | Autorização de Requisição | ⚠️ skip | — | — | [log] |

**Detalhes do relatório:**
- Testes filtrados por incompatibilidade de cliente não aparecem
- Testes que aparecem mais de uma vez são numerados: `[1/2]`, `[2/2]`
- O link `[trace]` abre o trace do Playwright no navegador
- O link `[log]` expande o log inline ou abre em nova aba
- A mensagem de erro (ex: texto do alerta vermelho do ASI via `RuntimeError`)
  aparece resumida na tabela, com opção de expandir o traceback completo

---

## Categorias de resultado

| Símbolo | Categoria | Aparece no relatório? | Descrição |
|---|---|---|---|
| ✅ | Passou | Sim | Tudo certo na primeira tentativa |
| ✅🔁 | Retentou e passou | Sim | Passou, mas o flow pode ser robustecido |
| ❌ | Falhou | Sim | Falha definitiva ou esgotou tentativas |
| ❌🔁 | Retentou e falhou | Sim | Falha persistente após N tentativas |
| ⚠️ | Skip explícito | Sim | `pytest.mark.skip` no código — evento intencional |
| — | Não disponível para cliente | **Não** | Filtrado silenciosamente pelo catálogo |

---

## CLI (`sentinela.py`)

```bash
# Roda para um cliente específico
python sentinela.py --cliente tcerj

# Roda para todos os clientes do configs.yaml, sequencialmente
python sentinela.py --todos

# Roda um único teste em todos os clientes (útil ao fabricar um novo teste)
python sentinela.py --teste tests/almoxarifado/movimentacao_interna/test_entrada_simples.py

# Roda um único teste em um cliente específico
python sentinela.py --teste tests/.../test_entrada_simples.py --cliente tcerj

# Simula a execução sem rodar nada — mostra o que seria executado e avisos
python sentinela.py --cliente tcerj --dry-run

# Sobrescreve configurações do config.yaml para este run
python sentinela.py --cliente tcerj --tentativas 2 --ttl 14

# Ambiente (raramente necessário — padrão é sempre qas)
python sentinela.py --cliente tcerj --ambiente prod

# Apaga todos os runs salvos
python sentinela.py --limpar

# Mostra todos os comandos disponíveis para a Sentinela
python sentinela.py --ajuda
```

**Nota sobre `--teste`:** nesse modo, a `ordem.yaml` é ignorada. O teste é
executado diretamente, sem verificar pré-requisitos de sequência. A filtragem
pelo `modules_catalog` ainda se aplica — se o teste não estiver disponível para
um cliente, é pulado silenciosamente.

**Nota sobre `--dry-run`:** exibe os testes que seriam executados para o cliente,
os testes que seriam ignorados por incompatibilidade, os testes do catálogo
ausentes da `ordem.yaml`, e paths inválidos na `ordem.yaml`. Nenhum browser
é aberto.

---

## Persistência e TTL (`storage.py`)

Cada run é salvo em `sentinela/reports/{data}_{hora}_{cliente}/`.
Na inicialização de qualquer execução, a Sentinela varre todos os diretórios
de reports e remove os que ultrapassaram o TTL configurado.

O comando `--limpar` apaga todos os runs independente do TTL.

---

## Plano de implementação

### Fase 1 — Fundação (sem execução real)
**Objetivo:** projeto inicializado, lê o catálogo, filtra corretamente por cliente.

1. Criar a estrutura de diretórios e arquivos vazios
2. Implementar `catalog_reader.py` — lê o `modules_catalog` e retorna o set
   de paths disponíveis por cliente, considerando `meta.clients`,
   `clients` e `exclude_clients`
3. Implementar leitura de `ordem.yaml` e filtragem por cliente
4. Implementar validação de cobertura — testes no catálogo ausentes da `ordem.yaml`

**Entregável:** `python sentinela.py --cliente tcerj --dry-run` mostra a lista
de testes que seriam executados, os ignorados, e os ausentes da ordem.

---

### Fase 2 — Execução e coleta de resultados
**Objetivo:** executa testes reais e coleta resultado, log e trace.

5. Implementar `executor.py` — escreve o cliente no `configs.local.yaml`,
   chama pytest via subprocess, captura stdout/stderr e código de saída,
   restaura o `configs.local.yaml` ao original
6. Implementar `storage.py` — cria diretório do run, salva logs numerados,
   move traces, TTL e limpeza automática na inicialização
7. Implementar `runner.py` — itera a lista filtrada, chama executor, agrega resultados
8. Implementar o CLI básico: `--cliente`, `--todos`, `--ambiente`, `--limpar`

**Entregável:** rodar a Sentinela contra um cliente real e encontrar os arquivos
de log e trace em `sentinela/reports/`.

---

### Fase 3 — Retry
**Objetivo:** não retentar o que não vale, retentar o que vale.

9. Implementar classificação de erros no `runner.py` — transiente vs. definitivo
   com base nas strings do traceback
10. Integrar retry com intervalo fixo de 10s entre tentativas
11. Numerar tentativas nos nomes dos arquivos de log

**Entregável:** provocar um timeout intencional e ver a Sentinela retentar corretamente.

---

### Fase 4 — Relatório HTML
**Objetivo:** resultado consultável e navegável.

12. Implementar `reporter.py` — gera `report.html` com tabela de resultados
13. Links para logs e traces funcionando
14. Expandir/colapsar traceback inline
15. Mensagem de erro resumida na tabela (especialmente o texto do `RuntimeError`)
16. Cabeçalho com resumo (passou/falhou/retentou/skip)

**Entregável:** abrir o `report.html` no navegador e navegar pelos resultados.

---

### Fase 5 — Polimento e CLI completo
**Objetivo:** ferramenta pronta para uso regular.

17. Flags `--tentativas`, `--ttl`, `--dry-run`, `--teste`
18. Saída no terminal durante execução com progresso em tempo real
19. Validação de paths inválidos na `ordem.yaml` (avisa se um path não existe no disco)

**Entregável:** ferramenta completa, usável sem consultar a documentação.

---

## Arquivos necessários como contexto no projeto Claude

Incluir no projeto Sentinela ao criá-lo no Claude:

| Arquivo | Localização | Por quê |
|---|---|---|
| Este documento | — | Planejamento completo |
| `modules_catalog.py` | gui/catalog/ | Fonte de filtragem por cliente |
| `configs.yaml` | configs/configs.yaml | Estrutura de clientes e ambientes |
| `conftest.py` | raiz do projeto | Como o pytest carrega o cliente ativo |
| `trace.py` | `utils/` | Como e onde o trace é salvo em falha |

Incluir somente se necessário durante a implementação:

| Arquivo | Por quê pode ser necessário |
|---|---|
| `utils/logger_config.py` | Se surgir dúvida sobre o sistema de logs |
| `utils/data_loader.py` | Se surgir dúvida sobre como o YAML é carregado |
| `utils/logging_manager.py` | Se surgir dúvida sobre o gerenciamento de logs por teste |
| Qualquer `test_*.py` | Se o Claude precisar ver o padrão real de um teste |
