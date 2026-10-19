from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global

def nova_transferencia_externa(page: Page) -> None:
    logger.info("Iniciou criação de nova Transferência Externa.")

    ctx = escopo(page)

    ctx.locator("button[name='submitNew']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou criação de nova Transferência Externa.")