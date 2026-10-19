from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def finalizar_solicitacao_materiais(page: Page) -> None:
    logger.info("Iniciou finalização de solicitação de materiais.")

    ctx = escopo(page)
    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou solicitação de materiais.")
