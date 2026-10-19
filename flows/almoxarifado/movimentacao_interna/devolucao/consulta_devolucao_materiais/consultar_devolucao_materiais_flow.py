from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def consultar_devolucao_materiais(page: Page, almoxarifado: dict[str, str]) -> None:
    logger.info("Iniciou consulta de devolução de materiais no almoxarifado '{}'.", almoxarifado["nome"])

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Preenchendo sigla do almoxarifado: '{}'.", almoxarifado["sigla"])
    preencher_campo(ctx, "input[name='model-2']", almoxarifado["sigla"])
    aguardar_ajax_global(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de devolução de materiais no almoxarifado '{}'.", almoxarifado["nome"])
