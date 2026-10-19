from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_formacao(page: Page, ug: dict[str, str]) -> None:
    logger.info("Iniciou consulta de formação de comissão de inventário pelo campo de UG: '{}'.", ug["codigo"])
 
    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)
    logger.info("Filtrando formação de comissão de inventário pelo campo de UG: '{}'.", ug["codigo"])
    ctx.locator("input[name='model-1']").fill(ug["codigo"])
    ctx.locator("button[name='lookup-model-1']").click()
    aguardar_ajax_global(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de formação de comissão de inventário pelo campo de UG: '{}'.", ug["codigo"])
