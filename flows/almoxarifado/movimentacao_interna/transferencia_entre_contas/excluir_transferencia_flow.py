from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def excluir_transferencia(page: Page) -> None:
    logger.info("Iniciou exclusão de transferência.")

    ctx = escopo(page)

    ctx.locator("button[name='submitBack']").click()
    aguardar_ajax_global(page)

    ctx.locator("button[name='submitBack']").click()
    aguardar_ajax_global(page)

    page.once("dialog", lambda dialog: dialog.accept())
    ctx.locator("button[name='submitDelete']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou exclusão de transferência.")
