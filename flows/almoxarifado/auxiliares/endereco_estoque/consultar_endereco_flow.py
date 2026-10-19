from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_endereco(page: Page, almoxarifado_data: dict[str, str], endereco: str) -> None:
    logger.info("Iniciou consulta de endereço de estoque '{}'.", endereco)

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Consultando sigla do almoxarifado '{}'.", almoxarifado_data["sigla"])
    ctx.type("input[name='model-1']", almoxarifado_data["sigla"])
    ctx.click("button[name='lookup-model-1']")
    aguardar_ajax_global(page)

    logger.info("Consultando endereço de estoque '{}'.", endereco)
    ctx.type("input[name='model-3']", endereco)
    ctx.click("button[name='submitSearch']")
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de endereço de estoque '{}'.", endereco)
