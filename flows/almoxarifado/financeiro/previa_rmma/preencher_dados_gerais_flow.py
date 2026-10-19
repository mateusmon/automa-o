from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def preencher_dados_gerais(page: Page, almoxarifado: dict, ug: dict) -> None:
    logger.info("Iniciou preenchimento de dados gerais de Prévia RMMA.")

    ctx = escopo(page)

    if ctx.locator('input[name="cdAlmoxarifado"]').is_visible():
        logger.info("Preenchendo sigla do almoxarifado '{}'.", almoxarifado["sigla"])
        preencher_campo(ctx, 'input[name="cdAlmoxarifado"]', almoxarifado["sigla"])
    else:
        logger.info("Preenchendo código da UG '{}'.", ug["codigo"])
        preencher_campo(ctx, 'input[name="cdUg"]', ug["codigo"])

    ctx.get_by_role("button", name="Imprimir").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou preenchimento de dados gerais de Prévia RMMA.")
