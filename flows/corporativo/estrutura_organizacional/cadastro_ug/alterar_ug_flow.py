from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, escolher_cidade, esperar_sucesso_ou_erro


def alterar_ug(page: Page, ug: dict) -> None:
    """
    Altera a U.G. invertendo o rádio Administração Direta (`inAdmDireta`) e o RESTAURA
    ao valor original (duas confirmações). Escolhe-se o rádio (campo sem restrição de
    unicidade) para não colidir com a chave.

    Ao carregar o registro via Anexar, o lookup da Cidade (`cdCidade`) não repopula; por
    isso a Cidade é re-selecionada antes de cada confirmação — sem isso o submit falha na
    validação.

    Cenário A. Pressupõe que o registro já foi carregado (ver `selecionar_ug`).
    """
    logger.info("Iniciou alteração de UG - Unidade Gestora: '{}'.", ug["codigo"])

    ctx = escopo(page)

    atual = "S" if ctx.locator("input[name='inAdmDireta'][value='S']").is_checked() else "N"
    outro = "N" if atual == "S" else "S"

    ctx.locator(f"input[name='inAdmDireta'][value='{outro}']").check()
    escolher_cidade(ctx, ug["cidade"])
    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou alteração de UG - Unidade Gestora: '{}'.", ug["codigo"])
