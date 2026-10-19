import os
from pathlib import Path
from typing import Any

import pytest
from loguru import logger
from playwright.sync_api import expect, sync_playwright

from domain.contexto_cliente import ContextoCliente
from utils import evidencia, historico_testes, logging_manager, modo, trace, versao
from utils.data_loader import load_data
from utils.logger_config import configure_logger

# Velocidade controlada pela GUI via variável de ambiente.
# Fallback para 0 (sem atraso) se executado direto pelo terminal.
PADRAO = int(os.environ.get("ASI_SLOW_MO", 0))
args_base = ["--start-maximized", "--disable-extensions"]
args_headless = ["--disable-pdfium", "--disable-features=PdfViewer"]


def pytest_addoption(parser):
    parser.addoption("--headless", action="store_true", default=False)


def pytest_configure(config):
    global HEADLESS
    HEADLESS = config.getoption("--headless", default=False)
    config.addinivalue_line(
        "markers",
        "trace_por_combinacao: o teste grava trace por trecho (chunk) e salva só os que falharem.",
    )


HEADLESS = (
    False  # default; sobrescrito pelo pytest_configure quando --headless é passado
)

CLIENTE_ATIVO = None  # definido no pytest_sessionstart, a partir de configs.yaml
HISTORICO_RESULTADOS = {}  # acumula resultado por teste durante a sessão, para gravar no sessionfinish


@pytest.fixture(scope="session")
def browser_session():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=HEADLESS,
            args=args_base + (args_headless if HEADLESS else []),
            slow_mo=PADRAO,
        )

        yield browser

        browser.close()


@pytest.fixture
def page(browser_session):
    context = browser_session.new_context(no_viewport=True, accept_downloads=True)

    trace.iniciar_trace(context)

    page = context.new_page()
    page.bring_to_front()

    expect.set_options(timeout=30_000)
    page.set_default_timeout(60_000)
    page.set_default_navigation_timeout(60_000)

    evidencia.set_page(page)

    yield page

    context.close()


def carregar_config_cliente():
    path_config = Path(__file__).resolve().parent / "configs" / "configs.yaml"

    if not path_config.exists():
        raise FileNotFoundError(f"Cliente não encontrado: {path_config}")

    config = load_data(path_config)

    path_local = path_config.parent / "configs.local.yaml"
    if path_local.exists():
        local = load_data(path_local)
        for chave in (
            "cliente_ativo",
            "ambiente",
            "usuario_local",
            "funcionario_local",
        ):
            if chave in local:
                config[chave] = local[chave]

    cliente_por_execucao = os.environ.get("ASI_CLIENTE_ATIVO")

    if cliente_por_execucao:
        config["cliente_ativo"] = cliente_por_execucao

    return config


def carregar_dados_cliente_ativo():
    config = carregar_config_cliente()

    cliente_ativo = config.get("cliente_ativo")
    if not cliente_ativo:
        raise ValueError("'cliente_ativo' não foi definido em configs.yaml")

    clientes = config.get("clientes", {})
    if cliente_ativo not in clientes:
        raise ValueError(
            f"Cliente '{cliente_ativo}' não foi encontrado em configs.yaml"
        )

    cliente_config = clientes[cliente_ativo]

    arquivo_dados = cliente_config.get("arquivo_dados")
    if not arquivo_dados:
        raise ValueError(f"Não há arquivo_dados para o cliente '{cliente_ativo}'")

    path_dados = Path(__file__).resolve().parent / arquivo_dados
    if not path_dados.exists():
        raise FileNotFoundError(
            f"Arquivo de dados do cliente não encontrado: {path_dados}"
        )

    dados_cliente = load_data(path_dados)

    if not dados_cliente:
        raise ValueError(f"Nenhum dado configurado no arquivo {path_dados}")

    ambiente = config.get("ambiente")
    if not ambiente:
        raise ValueError("'ambiente' não foi definido em configs.yaml")

    ambientes = cliente_config.get("ambientes", {})
    if ambiente not in ambientes:
        raise ValueError(
            f"Ambiente '{ambiente}' não configurado para o cliente '{cliente_ativo}'"
        )

    ambiente_config = ambientes[ambiente]

    url = ambiente_config.get("url")
    usuarios = ambiente_config["usuarios"]
    usuario_local = config.get("usuario_local") or []
    if isinstance(usuario_local, dict):
        usuario_local = [usuario_local]

    if usuario_local:
        local = usuario_local[0]
        usuario = (
            local.get("usuario")
            or local.get("login")
            or local.get("codigo_funcionario")
            or local.get("matricula")
        )
        senha = local.get("senha")
        if not senha:
            raise ValueError(
                f"Senha local não configurada para o cliente '{cliente_ativo}' no ambiente '{ambiente}'"
            )
    else:
        primeiro_usuario = next(iter(usuarios.values()))
        usuario = primeiro_usuario["usuario"]
        senha = primeiro_usuario["senha"]

    if not url:
        raise ValueError(
            f"URL não configurada para cliente '{cliente_ativo}' no ambiente '{ambiente}'"
        )

    if not usuario:
        raise ValueError(
            f"Usuário não configurado para cliente '{cliente_ativo}' no ambiente '{ambiente}'"
        )

    if not senha:
        raise ValueError(
            f"Senha não configurada para cliente '{cliente_ativo}' no ambiente '{ambiente}'"
        )

    dados_cliente.setdefault("dados_cliente", {})
    dados_cliente["dados_cliente"]["cliente"] = cliente_ativo
    dados_cliente["dados_cliente"]["url"] = url
    dados_cliente["dados_cliente"]["usuario"] = usuario
    dados_cliente["dados_cliente"]["senha"] = senha

    usuario_local = config.get("usuario_local") or []
    if isinstance(usuario_local, dict):
        usuario_local = [usuario_local]
    dados_cliente["_usuario_local"] = usuario_local

    funcionario_local = config.get("funcionario_local") or []
    if isinstance(funcionario_local, dict):
        funcionario_local = [funcionario_local]
    dados_cliente["_funcionario_local"] = funcionario_local

    # Preserva todas as credenciais do ambiente para cenários que exigem um
    # papel específico, como a preparação de massa do Genesis. A chave interna
    # evita colisão com `usuarios`, que no blueprint representa usuários a
    # serem cadastrados no ASI.
    dados_cliente["_credenciais_ambiente"] = usuarios

    unidade_gestora = cliente_config.get("unidade_gestora")
    if unidade_gestora and unidade_gestora.get("nome") and unidade_gestora.get("sigla"):
        dados_cliente["unidade_gestora"] = unidade_gestora

    ul_estoque = cliente_config.get("unidade_localizacao_estoque")
    if ul_estoque and ul_estoque.get("codigo"):
        dados_cliente["unidade_localizacao_estoque"] = ul_estoque

    return dados_cliente


@pytest.fixture(scope="session")
def contexto_cliente():
    dados = carregar_dados_cliente_ativo()
    return ContextoCliente(dados)


@pytest.fixture
def posicao_ordem() -> int:
    """Posição (1-based) desta chamada do teste na lista `ordem` do ordem.yaml.
    Fora do runner da Sentinela (execução direta/local), assume 1."""
    return int(os.environ.get("ASI_POSICAO_ORDEM", 1))


def pytest_sessionstart(session):
    """
    Hook do pytest chamado no início de uma sessão de testes.

    Este hook é executado **antes de qualquer teste** ser iniciado,
    permitindo inicializar recursos necessários para toda a sessão.

    Funcionalidade:
    - Chama `evidencia.iniciar()` para iniciar a captura de evidências
      (como logs, screenshots ou relatórios) antes da execução dos testes.

    Parâmetros:
    - session: objeto que representa a sessão de testes do pytest.
    """
    configure_logger()

    raiz_projeto = Path(__file__).resolve().parent
    execution_id = os.environ.get("ASI_EXECUTION_ID")
    namespace = execution_id if execution_id and execution_id.isalnum() else None
    path_evidencia = (
        raiz_projeto / "evidencia" / namespace
        if namespace
        else raiz_projeto / "evidencia"
    )
    path_logger = (
        raiz_projeto / "logs" / namespace if namespace else raiz_projeto / "logs"
    )
    path_trace = (
        raiz_projeto / "trace" / namespace if namespace else raiz_projeto / "trace"
    )

    path_evidencia.mkdir(parents=True, exist_ok=True)

    evidencia.iniciar(path_evidencia)
    logging_manager.iniciar(path_logger)
    trace.iniciar(path_trace)

    config = carregar_config_cliente()
    cliente_ativo = config["cliente_ativo"]
    v = config["clientes"][cliente_ativo].get("versao", 3)
    versao.set_versao(v)
    modo.set_headless(HEADLESS)

    global CLIENTE_ATIVO
    CLIENTE_ATIVO = cliente_ativo


def pytest_runtest_setup(item):
    logging_manager.iniciar_teste(item.nodeid)


def _executar_com_seguranca(descricao: str, acao) -> None:
    """
    Executa uma etapa de coleta de evidência sem deixar que ela derrube a sessão.

    Exceções levantadas dentro de um hook de report viram INTERNALERROR no pytest
    e matam a execução inteira — junto com o relatório da falha e com as demais
    evidências. Coleta de evidência é best-effort: se falhar, loga e segue.

    Parâmetros:
    - descricao: o que estava sendo feito, usado na mensagem de aviso.
    - acao: função sem argumentos que executa a etapa.
    """
    try:
        acao()
    except Exception as e:
        logger.warning("Falha ao {}: {}", descricao, e)


def _nome_do_artefato(item) -> str:
    """
    Converte o nodeid do teste em um nome de arquivo válido no Windows.

    Usa o nodeid completo (arquivo + nome do teste) para que dois testes do
    mesmo arquivo não sobrescrevam a evidência um do outro.
    """
    nome = item.nodeid.replace("::", "__").replace("/", "_").replace(os.sep, "_")

    for caractere in '<>:"\\|?*':
        nome = nome.replace(caractere, "_")

    return nome


def _logar_erro_do_flow(call) -> None:
    """
    Registra no arquivo de log o ponto exato do flow onde o teste quebrou.

    Percorre o traceback do fim para o início e para no primeiro frame que
    pertence a um flow — que é o que interessa para diagnosticar a falha.
    """
    if not call.excinfo:
        return

    # Percorre os frames do final para o início (começando do erro real)
    for frame in reversed(call.excinfo.traceback):
        # Filtra apenas arquivos flows
        if "flows" not in str(frame.path):
            continue

        # apenas_arquivo=True: vai para o arquivo de log, não para o stdout/GUI
        logger.bind(apenas_arquivo=True).error(
            f'\nArquivo "{frame.path}", linha {frame.lineno + 1}\n'
            f'Função "{frame.name}"\n'
            f"{frame.statement}\n"
            f"{call.excinfo.type.__name__}: {call.excinfo.value}"
        )
        break


def _salvar_trace_do_teste(item) -> None:
    """
    Salva o trace do Playwright com um nome próprio por teste.

    Testes que não usam a fixture `page` simplesmente não têm trace.
    Testes com o marker `trace_por_combinacao` já salvaram os chunks que
    falharam durante a execução, então não geram o trace inteiro.
    """
    if item.get_closest_marker("trace_por_combinacao"):
        logger.debug("Teste com trace por combinação. Trace global não será salvo.")
        return

    page = item.funcargs.get("page")

    if page is None:
        logger.debug("Teste sem fixture 'page'. Trace não será salvo.")
        return

    trace.salvar_trace(page.context, _nome_do_artefato(item))


def _extrair_modulo(nodeid: str) -> str:
    caminho_arquivo = nodeid.split("::")[0]
    partes = caminho_arquivo.split("/")[:-1]

    if partes and partes[0] == "tests":
        partes = partes[1:]

    return "/".join(partes) if partes else "geral"


def pytest_runtest_logreport(report):
    houve_skip_no_setup = report.when == "setup" and report.skipped
    if report.when != "call" and not houve_skip_no_setup:
        return

    resultado = "skip" if report.skipped else ("fail" if report.failed else "pass")

    HISTORICO_RESULTADOS[report.nodeid] = {
        "modulo": _extrair_modulo(report.nodeid),
        "resultado": resultado,
    }


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Hook do pytest que é chamado após cada execução de teste.

    Este hook permite inspecionar o resultado de cada teste e executar ações
    adicionais, como registrar evidências em caso de falha.

    Parâmetros:
    - item: objeto do teste, contém informações como nome e parâmetros.
    - call: objeto que representa a execução do teste (setup, call ou teardown).

    Funcionalidade:
    - Aguarda a execução do teste com `yield`.
    - Obtém o relatório do teste com `outcome.get_result()`.
    - Se o teste falhar durante a fase de execução ("call"), coleta as evidências
      da falha (log do erro, trace, screenshot) e as persiste.

    A ordem da coleta é intencional: primeiro o que não depende do browser (log),
    depois o que depende só do servidor do Playwright (trace) e por último o
    screenshot, que é a etapa mais frágil por depender da página responder. Cada
    etapa é isolada para que a falha de uma não impeça as outras.
    """
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        logger.error("Teste {} falhou, coletando evidências.", item.nodeid)

        _executar_com_seguranca(
            "registrar erro do flow", lambda: _logar_erro_do_flow(call)
        )
        _executar_com_seguranca("salvar trace", lambda: _salvar_trace_do_teste(item))
        _executar_com_seguranca(
            "capturar screenshot",
            lambda: evidencia.screenshot(f"falha-{_nome_do_artefato(item)}"),
        )

        _executar_com_seguranca("finalizar evidência", evidencia.finalizar_evidencia)

    if report.when == "teardown":
        _executar_com_seguranca("finalizar evidência", evidencia.finalizar_evidencia)
        logging_manager.finalizar_teste()


def pytest_sessionfinish(session, exitstatus):
    """
    Hook do pytest chamado no final da sessão de testes.

    Este hook é executado **depois que todos os testes foram concluídos**,
    permitindo executar ações de finalização ou limpeza de recursos.

    Funcionalidade:
    - Imprime no console o código de saída da sessão para fins de depuração.
    - Grava em HISTORICO_RESULTADOS o resultado mais recente de cada teste
      rodado nesta sessão, no arquivo JSON do cliente ativo (independe de
      exitstatus — falhas também precisam ficar registradas).
    - Se todos os testes passaram (exitstatus == 0), chama
      `evidencia.cleanup()` para limpar registros temporários de evidência.

    Parâmetros:
    - session: objeto que representa a sessão de testes do pytest.
    - exitstatus: código de saída do pytest indicando o resultado da sessão.
      - 0: todos os testes passaram
      - 1: falha em algum teste
      - 2: interrupção ou erro de configuração
      - Outros valores: erros específicos do pytest
    """
    print(f"pytest_sessionfinish called: {exitstatus}")

    if HISTORICO_RESULTADOS:
        _executar_com_seguranca(
            "registrar histórico de testes",
            lambda: historico_testes.atualizar_lote(
                CLIENTE_ATIVO, HISTORICO_RESULTADOS
            ),
        )

    if exitstatus == 0:
        evidencia.cleanup()
        trace.cleanup()


GENESIS_DIR = (Path(__file__).resolve().parent / "tests" / "genesis").resolve()


def _eh_teste_genesis(node: Any) -> bool:
    """Informa se o nó do pytest pertence ao conjunto novo do Genesis."""
    try:
        return Path(str(node.path)).resolve().is_relative_to(GENESIS_DIR)
    except (AttributeError, OSError, RuntimeError):
        return False


def _deve_pausar_na_falha(node: Any) -> bool:
    """Decide se a falha deve abrir a pausa interativa do Playwright."""
    if HEADLESS:
        return False

    if _eh_teste_genesis(node):
        return True

    return os.environ.get("ASI_PAUSAR_NA_FALHA", "0") == "1"


def pytest_exception_interact(node: Any, call: Any, report: Any) -> None:
    """Pausa a página após uma falha, antes do teardown fechar o contexto."""
    if not _deve_pausar_na_falha(node):
        return

    if getattr(node, "_asi_pausa_realizada", False):
        return

    page = getattr(node, "funcargs", {}).get("page")
    if page is None:
        return

    node._asi_pausa_realizada = True
    logger.warning(
        "Erro em {} ({}). Execução pausada; clique em Resume no Inspector para continuar.",
        node.nodeid,
        call.when,
    )
    try:
        page.pause()
    except Exception as e:
        logger.debug("Pausa do Playwright encerrada: {}", e)
