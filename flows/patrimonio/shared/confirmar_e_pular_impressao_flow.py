from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def confirmar(page: Page) -> None:
    logger.info("Iniciou confirmação de movimentação.")

    ctx = escopo(page)

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    
    logger.info("Finalizou confirmação de seleção.")
