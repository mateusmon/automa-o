from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def autorizar_requisicao(page: Page) -> None:
    logger.info("Iniciou autorização de requisição.")

    ctx = escopo(page)
    _autorizar(ctx, page)

    logger.info("Finalizou autorização de requisição.")


def _autorizar(ctx, page: Page) -> None:
    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)
