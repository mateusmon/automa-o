from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def consultar_recebimento(page: Page, almoxarifado: dict[str, str]) -> None:
    logger.info("Iniciou consulta de recebimento de transferência entre almoxarifados.")

    ctx = escopo(page)
    _consultar(ctx, page, almoxarifado)

    logger.info("Finalizou consulta de recebimento de transferência entre almoxarifados.")


def _consultar(ctx, page: Page, almoxarifado: dict[str, str]) -> None:
    ctx.click("button[name='submitTabSearchData']")
    aguardar_ajax_global(page)

    logger.info("Preenchendo sigla do almoxarifado: '{}'.", almoxarifado["sigla"])
    preencher_campo(ctx, "input[name='model-0']", almoxarifado["sigla"])
    logger.info("Preenchendo status da transferência: 'FINALIZADA'.")
    preencher_campo(ctx, "input[name='model-10']", "FINALIZADA")

    ctx.click("button[name='submitSearch']")
    aguardar_ajax_global(page)
