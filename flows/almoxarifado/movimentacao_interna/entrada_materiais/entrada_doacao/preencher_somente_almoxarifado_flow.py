from playwright.sync_api import Page, expect
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def preencher_somente_almoxarifado(page: Page, almoxarifado: dict) -> None:
    logger.info("Iniciou preenchimento de almoxarifado '{}'.", almoxarifado["nome"])

    ctx = escopo(page)
    _preencher(ctx, page, almoxarifado)

    logger.info("Finalizou preenchimento de almoxarifado '{}'.", almoxarifado["nome"])


def _preencher(ctx, page: Page, almoxarifado: dict) -> None:
    while ctx.locator("input[name='almoxarifado']").input_value() == "":
        logger.info("Preenchendo almoxarifado '{}'.", almoxarifado["nome"])
        preencher_campo(ctx, "#almoxarifado", almoxarifado["sigla"])
    aguardar_ajax_global(page)
    expect(ctx.locator('input[name="ug"]')).not_to_have_value("")
