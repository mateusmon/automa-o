from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def mostrar_suspensos(page: Page) -> None:
    logger.info("Iniciou exibição de UGs suspensas.")

    ctx = escopo(page)
    ctx.locator("input[name='mostraUGsSuspensas']").check()
    aguardar_ajax_global(page)

    logger.info("Finalizou exibição de UGs suspensas.")
