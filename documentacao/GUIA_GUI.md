# Guia da GUI (gui/)

Documentação da interface gráfica (Tkinter) usada para selecionar cliente/ambiente, provisionar dados (Genesis) e executar os testes sem depender do terminal.

## 1. Visão geral da arquitetura

```text
gui/
├── main.py                    # Entry point (com tratamento de erro de import)
├── app.py                     # Janela principal (classe App, extende tk.Tk)
├── app_icon.ico                # Ícone da aplicação
│
├── catalog/
│   └── modules_catalog.py     # Dict MODULES — catálogo estrutural de todos os testes
│
├── core/
│   ├── genesis_runner.py      # Sobe genesis/main.py como subprocess, parseia log JSON
│   ├── test_runner.py         # Sobe pytest como subprocess, faz streaming de stdout
│   ├── gui_log_sink.py        # Sink do Loguru que redireciona logs Python para a GUI
│   ├── module_filter.py       # Filtra MODULES pelo cliente ativo
│   └── style_config.py        # Tema ttk (cores, fontes)
│
├── components/                # Widgets reutilizáveis
│   ├── client_selector.py     # Seletor de Cliente / Ambiente / URL / Velocidade
│   ├── type_ahead_combobox.py # Combobox com busca rápida inteligente por digitação
│   ├── log_panel.py           # Painel de log colorido, expansível
│   ├── modulo_colapsavel.py   # Cabeçalho colapsável (▶/▼)
│   ├── scrollable_frame.py    # Container com scroll (canvas + scrollbar)
│   └── tooltip.py             # Tooltip simples on-hover
│
├── layout/                    # Componentes de layout específicos da página
│   ├── header.py              # Título/subtítulo estático
│   └── modules_builder.py     # Monta a árvore de seleção de testes a partir do catálogo
│
├── services/
│   └── config_services.py     # Leitura/escrita de configs.yaml + configs.local.yaml
│
└── icons/                     # Ícones dos módulos (Almoxarifado, Patrimônio, Corporativo)
```

### Responsabilidade por camada

| Camada         | Responsabilidade                                                            |
|----------------|-----------------------------------------------------------------------------|
| `catalog/`     | Definição estrutural pura dos testes disponíveis (nenhuma lógica de UI)     |
| `core/`        | Execução (subprocess de pytest/Genesis) e infraestrutura de log             |
| `components/`  | Widgets Tkinter reutilizáveis, sem conhecimento do domínio ASI              |
| `layout/`      | Composição de componentes em seções específicas da tela                     |
| `services/`    | Acesso a configuração persistida (YAML)                                     |

## 2. Como a GUI é executada

```text
app.bat / app.vbs  →  .venv\Scripts\pythonw.exe gui\main.py
```

- `app.bat`: batch simples, executa o Python da venv apontando para `gui/main.py`.
- `app.vbs`: wrapper VBScript que chama o mesmo comando sem abrir janela de console.
- `gui/main.py`: importa `App` de `gui/app.py`, instancia e chama `App().mainloop()`. Qualquer falha de import é logada em `erro_inicializacao.log` (para diagnosticar ambientes sem dependências instaladas).
- `gui/app.py`: classe `App(tk.Tk)` — define título "ASI Automação 2.0", ícone, tamanho inicial 1000x700 e abre maximizada (`state("zoomed")`).

## 3. Configuração de cliente/ambiente (services/config_services.py)

A GUI lê e escreve dois arquivos:

- **`configs/configs.yaml`** — definição-base dos clientes (label, versão, URLs por ambiente, usuários). Editável pela GUI apenas no campo de URL.
- **`configs/configs.local.yaml`** — estado de execução local e não versionado (`cliente_ativo`, `ambiente` selecionados). Sobrescreve o `configs.yaml` sem alterá-lo.

`ConfigService`:

```python
config = ConfigService("configs/configs.yaml")

config.get_cliente_ativo()           # local > base
config.get_ambiente()
config.get_clientes()                # dict completo de clientes

config.set_cliente_ativo("pcdfv4")   # grava em configs.local.yaml
config.set_ambiente("qas")
config.update_client_url("pcdfv4", "qas", nova_url)  # grava em configs.yaml
```

Escritas são feitas em arquivo temporário e movidas atomicamente, para não corromper o YAML se o processo for interrompido. Um dumper customizado garante que strings numéricas (CPF, matrícula) não sejam convertidas para `int` ao salvar.

Fluxo em `app.py`: ao trocar o cliente no combobox, `_on_client_changed()` repopula o combobox de ambiente e a URL exibida; ao trocar o ambiente, `_on_ambiente_changed()` atualiza a URL; editar a URL habilita um botão "Salvar" que chama `update_client_url`.

## 4. Catálogo de testes (catalog/modules_catalog.py)

Arquivo de **dados puros** (~1400 linhas, sem lógica de UI): um dict `MODULES` com 3 módulos (`Almoxarifado`, `Patrimônio`, `Corporativo`), cada um dividido em seções, cada seção com uma lista de testes:

```python
MODULES = {
    "Almoxarifado": {
        "meta": {},  # opcional: {"clients": [...]} ou {"exclude_clients": [...]}
        "sections": {
            "Movimentação Interna": [
                {
                    "name": "Consulta de Material",
                    "path": "tests/almoxarifado/movimentacao_interna/test_consulta_material.py",
                    "exclude_clients": ["seadpb"],   # oculto para este cliente
                },
                # ...
            ],
        },
    },
    "Patrimônio": {...},
    "Corporativo": {...},
}
```

- `exclude_clients`: oculta o teste/módulo para os clientes listados.
- `clients`: torna o teste/módulo visível **apenas** para os clientes listados.
- `versao_maxima` (int): visível somente para clientes com `versao <= versao_maxima` (ex.: `3` = só v3).
- `versao_minima` (int): visível somente para clientes com `versao >= versao_minima` (ex.: `4` = v4 e acima).
- Essas regras podem estar no nível do teste ou no `meta` do módulo, e podem coexistir (o item só aparece se passar em todas as chaves presentes).

**Quando usar cada uma:** `clients`/`exclude_clients` são para exceções de um cliente específico (ex.: uma integração financeira própria de um órgão). `versao_minima`/`versao_maxima` são para quando o teste só existe em uma versão do GRP — nesse caso **não enumere os clientes daquela versão à mão**: com dezenas de clientes cadastrados, listar manualmente todos os v3 ou v4 (e lembrar de atualizar a lista a cada cliente novo) não escala e já causou inconsistência (clientes v4 esquecidos em listas antigas). Declarar a versão resolve automaticamente para qualquer cliente, presente ou futuro, com base no campo `versao` de `configs.yaml`.

```python
# Só existe na v3 — qualquer cliente v3, presente ou futuro
{"name": "Relatório de Empenho (v3)", "path": "...", "versao_maxima": 3}

# Só existe na v4+
{"name": "Relatório de Empenho (v4)", "path": "...", "versao_minima": 4}
```

**Convenção ao criar um novo teste** (ver também `documentacao/GUIA_TESTES.md`): registrar a entrada em `modules_catalog.py`, na seção correspondente:

```python
{
    "name": "Alteração de Configuração Lançamentos - Operações",
    "path": "tests/almoxarifado/auxiliares/test_alteracao_configuracao_lancamentos_operacoes.py",
},
```

Geralmente a ordem que os testes devem ficar é: Testes de cadastro, teste de consulta de cadastro, teste de alteração de cadastro, teste de exclusão de cadastro.

### Como o catálogo alimenta a tela

1. `app.py` importa `MODULES`.
2. `module_filter.filtrar_modulos_por_cliente(MODULES, client_id)` remove testes/seções/módulos não aplicáveis ao cliente ativo.
3. `ModulesBuilder` (em `layout/modules_builder.py`) recebe o catálogo já filtrado e constrói a árvore de UI:
   - Cada módulo → um cabeçalho colapsável (`ModuloColapsavel`).
   - Cada seção → título + checkbox mestre "Marcar todos".
   - Cada teste → checkbox individual (grid de 2 colunas).
4. Uma busca por substring (case-insensitive) filtra a árvore em tempo real, expandindo automaticamente os módulos com resultados e restaurando o estado anterior de expansão ao limpar a busca.
5. `modules_builder.get_selected_tests()` retorna a lista de `path`s marcados, usada para montar o comando pytest.

## 5. Execução de testes (core/test_runner.py)

Botão "Rodar Testes" → `app.run_tests()`:

1. Coleta os `path`s selecionados via `modules_builder.get_selected_tests()`.
2. Resolve caminhos absolutos e valida existência em disco.
3. Lê a velocidade (`slow_mo`) do `ClientSelector`.
4. Chama `test_runner.run(paths, slow_mo)`.

`TestRunner.run()` bloqueia nova execução se já houver uma em curso, trava a UI (`app._set_ui_running_state(True)`) e dispara uma thread daemon:

```python
cmd = [python_exe, "-m", "pytest", *test_files, "-x", "-p", "no:randomly"]

env["PYTHONUNBUFFERED"] = "1"
env["ASI_SLOW_MO"] = str(slow_mo)

subprocess.Popen(cmd, cwd=project_root, stdout=PIPE, stderr=STDOUT,
                  text=True, bufsize=1, env=env, creationflags=...)
```

- `-x`: para no primeiro erro. `-p no:randomly`: preserva a ordem escolhida na GUI.
- O stdout é lido linha a linha e enviado direto para `app.log(line, level)` — o nível (`INFO`/`ERROR`/`SUCCESS`/`WARNING`/`DEBUG`) é inferido por palavras-chave na própria linha (ex.: `"ERROR"`, `"FAILED"`, `"SUCCESS"`).
- Ao terminar, `_finish_execution()` reabilita a UI via `app.after(0, ...)` (callback seguro para a thread principal do Tkinter).

## 6. "Preparar Ambiente" — Genesis (core/genesis_runner.py)

Botão "Preparar Ambiente" → `app.run_genesis()` → `GenesisRunner.run(slow_mo)`:

```python
env["ASI_SLOW_MO"] = str(slow_mo)
subprocess.Popen([sys.executable, str(root_path / "genesis" / "main.py")],
                  env=env, stdout=PIPE, stderr=STDOUT, text=True)
```

Diferente do `TestRunner`, o Genesis emite **logs estruturados em JSON** (uma linha por evento), que o `GenesisRunner` parseia e reencaminha para o Loguru da GUI:

```python
log = json.loads(line)
formatted = f"{log['time']} | [GENESIS] | {log['level'].upper()} | {log['message']}"
getattr(logger, log['level'].lower(), logger.info)(formatted)
```

Linhas que não são JSON válido (ex.: saída inesperada) são logadas como texto puro (fallback). `GenesisRunner.stop()` mata a árvore de processos via `taskkill /F /T /PID <pid>` — necessário porque o Playwright do Genesis abre subprocessos próprios (Chromium) que não são filhos diretos do processo Python.

> Ver [`GUIA_GENESIS.md`](GUIA_GENESIS.md) para o funcionamento interno do próprio Genesis (rotinas, flows, services).

## 7. Outros componentes

| Componente | Arquivo | Função |
| --- | --- | --- |
| `ClientSelector` | `components/client_selector.py` | 4 linhas: Cliente, Ambiente, URL (editável), Velocidade (Rápido/Médio/Lento → `ASI_SLOW_MO`) |
| `TypeAheadCombobox` | `components/type_ahead_combobox.py` | Combobox com busca rápida por digitação com buffer e correspondência flexível |
| `LogPanel` | `components/log_panel.py` | Painel de log com cores por nível, auto-scroll (desliga se o usuário rolar para cima) e botão ▲/▼ para expandir |
| `ModuloColapsavel` | `components/modulo_colapsavel.py` | Cabeçalho ▶/▼ que mostra/esconde o corpo do módulo |
| `ScrollableFrame` | `components/scrollable_frame.py` | Canvas + scrollbar para a área de módulos |
| `Tooltip` | `components/tooltip.py` | Tooltip on-hover genérico |
| `Header` | `layout/header.py` | Título/subtítulo estático, sem lógica |

A velocidade selecionada (`Rápido`=0ms, `Médio`=750ms, `Lento`=1500ms) é propagada via variável de ambiente `ASI_SLOW_MO`, lida tanto por `conftest.py` (nos testes) quanto pelo Genesis.

## 8. Convenções de nomenclatura usadas na GUI

- Arquivos: `snake_case.py`.
- Classes: `PascalCase` (`App`, `ConfigService`, `ClientSelector`, `TypeAheadCombobox`, `ModuloColapsavel`, `GenesisRunner`, `TestRunner`, `LogPanel`).
- Métodos/atributos privados: prefixo `_` (`_build_ui`, `_on_client_changed`).
- Widgets: sufixo pelo tipo (`*_btn`, `*_combo`, `*_var`, `*_frame`, `*_label`).
- Constantes: `UPPER_CASE` (`MODULES`).
- Cor de marca: `#972121` (maroon); fonte padrão "Segoe UI"; monoespaçada "Consolas" para URLs/código.

## 9. O que NÃO fazer

- Não colocar lógica de negócio ou de execução de testes em `catalog/modules_catalog.py` — é dado estrutural puro.
- Não escrever diretamente em `configs.yaml` fora do `ConfigService` — usar sempre a escrita atômica para não corromper o arquivo.
- Não bloquear a thread principal do Tkinter com chamadas longas (pytest, Genesis) — sempre disparar em thread daemon e sincronizar de volta com `app.after(0, ...)`.
- Não esquecer de registrar um novo teste em `modules_catalog.py` ao criá-lo — sem isso ele não aparece na GUI (ver `documentacao/GUIA_TESTES.md`).
