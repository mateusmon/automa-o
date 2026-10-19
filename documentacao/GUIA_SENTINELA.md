# Guia do Sentinela (sentinela/)

Ferramenta CLI de auditoria: executa a suíte completa de testes (ou parte dela) para um ou todos os clientes, de forma sequencial e resiliente a falhas transitórias, gerando um relatório HTML consolidado.

## 1. Estrutura

```text
sentinela/
├── sentinela.py          # Entry point CLI (argparse)
├── runner.py             # Orquestra a execução por cliente (filtra, sequencia, tenta novamente)
├── executor.py           # Executa um único teste via subprocess de pytest
├── catalog_reader.py     # Lê gui/catalog/modules_catalog.py para saber quais testes valem por cliente
├── ordem_reader.py       # Lê e seleciona jornadas lógicas de ordem.yaml
├── reporter.py           # Gera o report.html do run
├── storage.py            # Cria diretórios de run, salva logs/traces, limpa runs antigos (TTL)
├── models.py             # dataclass ResultadoTeste
├── config.yaml           # tentativas / ttl_dias padrão
├── ordem.yaml            # Jornadas lógicas ordenadas (permite duplicatas propositalmente)
└── reports/              # Saída: um diretório por execução (YYYY-MM-DD_HHhMM_cliente/)
```

Não depende de `flows/`, `utils/`, `domain/` ou `genesis/` — só de `configs/`, do catálogo da GUI e dos arquivos de teste em si (executados via subprocess).

## 2. Como executar

```bash
python sentinela/sentinela.py --cliente tcerj              # todos os testes do cliente
python sentinela/sentinela.py --todos                       # todos os clientes, sequencialmente
python sentinela/sentinela.py --cliente tcerj --modulo tests/almoxarifado   # seleciona jornadas por prefixo
python sentinela/sentinela.py --teste tests/.../test_x.py --todos           # um teste, todos os clientes
python sentinela/sentinela.py --cliente tcerj --dry-run      # simula sem executar
python sentinela/sentinela.py --cliente tcerj --tentativas 2 --ttl 14 --headless
python sentinela/sentinela.py --cliente tcerj --pausa        # pausa na falha, para investigar
python sentinela/sentinela.py --limpar                       # apaga todos os runs salvos
python sentinela/sentinela.py --ajuda
python sentinela/sentinela.py --cliente tcerj --teste tests/.../test_x.py --count 100       # repete o mesmo teste N vezes
```

Com `--pausa`, o teste que falha chama `page.pause()` e aguarda o usuário clicar em Resume no
Inspector do Playwright. Sem a flag (padrão), a falha só coleta evidências e o navegador fecha,
que é o esperado ao rodar em lote. Os testes do Genesis novo (`tests/genesis/`) sempre usam a
pausa em falha quando executados com o navegador visível. Não há pausa interativa com
`--headless`. O Genesis antigo, executado pelo runner próprio em `genesis/`, conserva seu popup.

É uma ferramenta de terminal independente — **não** é iniciada por `app.bat`/GUI e não é chamada pelo `pytest` diretamente; ela é quem chama o `pytest` (via subprocess em `executor.py`).

Com `--count N`, você repete um único teste (`--teste` obrigatório) o número de vezes especificado. Todos os artefatos de repetição receberão um sufixo (ex: _r1, _r2) e as execuções entrarão na mesma lista de resultados, exibindo no resumo final as contagens exatas e em quais repetições houve falha (ótimo para estressar a estabilidade de um cenário).

## 3. Fluxo de execução

1. `sentinela.py` lê `configs/configs.yaml` (lista de clientes) e `sentinela/config.yaml` (`tentativas`, `ttl_dias`), aplicando overrides de `--tentativas`/`--ttl` se passados.
2. `runner.executar_para_cliente()`:
   - Lê as jornadas lógicas em `ordem_reader.ler_modulos()` (`ordem.yaml`) e seleciona os blocos de `--modulo`, quando informado.
   - Achata a jornada selecionada e filtra para os testes disponíveis ao cliente via `catalog_reader.testes_disponiveis_para(cliente_id)` — que reaproveita as regras `clients`/`exclude_clients` do `gui/catalog/modules_catalog.py`.
   - Para cada teste, chama `executor.executar_teste(...)`.
3. `executor.executar_teste()`:
   - Grava temporariamente `cliente_ativo: "<cliente_id>"` em `configs/configs.local.yaml`.
   - Roda `python -m pytest {path} -s --tb=long [--headless]` via subprocess.
   - Restaura o `configs.local.yaml` original ao final.
   - Se falhar por erro transitório (timeout de navegação, `net::ERR_*`, browser fechado), tenta novamente (até `tentativas`, com 10s de espera entre tentativas).
   - Em falha definitiva, move o trace do Playwright (de `trace/`) para o diretório do run.
4. `storage.criar_diretorio_run()` cria `sentinela/reports/YYYY-MM-DD_HHhMM_cliente/`; `salvar_log()` grava um `.log` por tentativa; `mover_trace()` move o `.zip` de trace.
5. `reporter.py` gera `report.html` no mesmo diretório, com tabela colorida por status e link para o trace viewer (`trace.playwright.dev`).
6. No início da execução, `storage.limpar_runs_antigos(ttl_dias)` remove runs com mais de N dias.

## 4. Status possíveis

| Símbolo | Status               | Significado                                    |
|---------|----------------------|------------------------------------------------|
| ✓       | `passou`             | Sucesso na primeira tentativa                  |
| ✓~      | `retentou_passou`    | Falhou por erro transitório, passou ao repetir |
| ✗       | `falhou`             | Falha definitiva na primeira tentativa         |
| ✗~      | `retentou_falhou`    | Falhou mesmo após todas as tentativas          |
| ⚠       | `skip`               | Pulado intencionalmente                        |

## 5. Arquivos de configuração

- **`sentinela/config.yaml`** — `tentativas` (padrão 3) e `ttl_dias` (padrão 7), sobrescrevíveis via CLI.
- **`sentinela/ordem.yaml`** — lista manual de jornadas lógicas (`modulos` → `modulo` + `ordem`). Um bloco pode conter paths de outra pasta quando eles preparam sua jornada. Duplicatas são permitidas de propósito (ex.: recriar dados entre blocos). Primeiro a Sentinela seleciona o bloco pelo `--modulo`; depois `runner.py` filtra os paths pelo cliente via `catalog_reader`.

## 6. O que NÃO fazer

- Não editar `ordem.yaml` para remover/duplicar testes sem entender o motivo da ordem atual — duplicatas costumam ser propositais (dependências entre cenários).
- Não mover pré-condições para outro bloco apenas porque seu path físico pertence a outra pasta: o bloco precisa executar isoladamente com suas dependências declaradas.
- Não usar o Sentinela como substituto do `pytest`/GUI para desenvolvimento local — ele é uma ferramenta de auditoria/regressão, roda a suíte inteira (ou grandes fatias) e é mais lento por design (retries, sequencial).
- Não esquecer que `configs/configs.local.yaml` é sobrescrito temporariamente durante a execução — se o processo for interrompido de forma abrupta (kill -9), o arquivo pode não ser restaurado; verificar `cliente_ativo` após uma execução interrompida.
