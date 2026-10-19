from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def restaurar_transferencia_externa(page: Page) -> None:
    logger.info("Iniciou restauração de Transferência Externa.")

    ctx = escopo(page)

    ctx.locator("button[name='submitRestore']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou restauração de Transferência Externa.")