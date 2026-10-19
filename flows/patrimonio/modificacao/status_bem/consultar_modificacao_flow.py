from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_modificacao(page: Page, ug_data: dict[str, str]) -> None:
    logger.info("Iniciou consulta de modificação de status de bem {}.", ug_data["codigo"])

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    ctx.locator("input[name='model-1']").fill(ug_data["codigo"])
    ctx.locator("button[name='lookup-model-1']").click()
    aguardar_ajax_global(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de modificação de status de bem {}.", ug_data["codigo"])
