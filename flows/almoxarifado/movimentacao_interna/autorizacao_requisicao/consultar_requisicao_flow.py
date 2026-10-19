from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_requisicao(page: Page) -> None:
    logger.info("Iniciou consulta de requisição.")

    ctx = escopo(page)
    ctx.locator("button[name='submitSearch']").click()

    aguardar_ajax_global(page)
    logger.info("Finalizou consulta de requisição.")
