from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import clicar_com_ajax, preencher_campo


def preencher_almoxarifado(page: Page, almoxarifado: dict) -> None:
    logger.info("Iniciou preenchimento de almoxarifado '{}'.", almoxarifado["sigla"])

    ctx = escopo(page)

    logger.info("Preenchendo sigla do almoxarifado '{}'.", almoxarifado["sigla"])
    preencher_campo(ctx, "input[name='listAlmoxs']", almoxarifado["sigla"])
    btn_search = ctx.locator("button[name='submitSearch']")
    clicar_com_ajax(ctx, btn_search)

    logger.info("Finalizou preenchimento de almoxarifado '{}'.", almoxarifado["sigla"])
