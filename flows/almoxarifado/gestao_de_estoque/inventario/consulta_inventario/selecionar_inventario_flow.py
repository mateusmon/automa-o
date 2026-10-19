from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def selecionar_inventario(page: Page, almoxarifado: dict) -> bool:
    logger.info("Iniciou seleção de inventário no almoxarifado '{}'.", almoxarifado["sigla"])

    ctx = escopo(page)

    linha = ctx.locator("table[name='paginationTable'] tbody tr").filter(
        has=ctx.locator("td").nth(1).filter(has_text=almoxarifado["nome"])
    ).first

    if linha.count() == 0:
        logger.info("Nenhum inventário encontrado para o almoxarifado '{}'.", almoxarifado["nome"])
        return False

    linha.locator("button[name='submitUse']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou seleção de inventário no almoxarifado '{}'.", almoxarifado["sigla"])
    return True
