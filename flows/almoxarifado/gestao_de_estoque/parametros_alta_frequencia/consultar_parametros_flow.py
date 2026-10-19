from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def consultar_parametros(page: Page, almoxarifado: dict) -> None:
    logger.info("Iniciou consulta de Parâmetros de Alta Frequência no almoxarifado '{}'.", almoxarifado["sigla"])

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Preenchendo sigla do almoxarifado '{}'.", almoxarifado["sigla"])
    preencher_campo(ctx, "input[name='model-1']", almoxarifado["sigla"])

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de Parâmetros de Alta Frequência no almoxarifado '{}'.", almoxarifado["sigla"])
