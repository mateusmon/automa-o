from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_conta_contabil(page: Page, bem: dict[str, str]) -> bool:
    logger.info("Iniciou consulta de Conta Contábil para o bem '{}' .", bem["nome"])

    ctx = escopo(page)

    ctx.click("button[name='submitSearch']")
    aguardar_ajax_global(page)

    ctx.click("button[name='submitSearch']")
    aguardar_ajax_global(page)

    rows = ctx.locator("table[name='paginationTable'] tbody tr")
    
    linha = rows.first
    if linha.count() == 0:
        logger.info("Nenhuma Conta Contábil encontrada para o bem '{}' .", bem["nome"])
        return False

    logger.info("Foi encontrada uma Conta Contábil para o bem '{}' .", bem["nome"])

    linha.locator("button[name='submitUse']").click()
    aguardar_ajax_global(page)
    logger.info("Finalizou consulta de Conta Contábil para o bem '{}' .", bem["nome"])
    return True
