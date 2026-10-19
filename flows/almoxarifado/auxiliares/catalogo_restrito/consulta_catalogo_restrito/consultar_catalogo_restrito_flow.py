from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_catalogo_restrito(page: Page, almoxarifado: dict[str, str]) -> None:
    logger.info("Iniciou consulta de catálogo restrito do almoxarifado '{}'.", almoxarifado)

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    # Preenche Almoxarifado
    logger.info("Consultando almoxarifado '{}'.", almoxarifado["sigla"])
    ctx.locator("input[name='model-1']").fill(almoxarifado["sigla"])
    ctx.locator("button[name='lookup-model-1']").click()
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de catálogo restrito do almoxarifado '{}'.", almoxarifado)
