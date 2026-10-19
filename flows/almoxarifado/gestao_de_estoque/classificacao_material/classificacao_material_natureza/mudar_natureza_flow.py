from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def mudar_natureza(page: Page) -> None:
    logger.info("Iniciou modificação de natureza do material.")

    ctx = escopo(page)

    ctx.locator("button[name='submitAdicionar']").click()
    aguardar_ajax_global(page)

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou modificação de natureza do material.")
