from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def selecionar_transferencia_entre_enderecos(page: Page, almoxarifado: dict) -> bool:
    logger.info("Iniciou seleção de transferência entre endereços no almoxarifado '{}'.", almoxarifado["nome"])

    ctx = escopo(page)

    linha = ctx.locator("table[name='paginationTable'] tbody tr").filter(
        has=ctx.locator("td").nth(1).filter(has_text=almoxarifado["nome"])
    ).first

    if linha.count() == 0:
        logger.info("Nenhuma transferência encontrada para o almoxarifado '{}'.", almoxarifado["nome"])
        return False

    linha.locator("button[name='submitUse']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou seleção de transferência entre endereços no almoxarifado '{}'.", almoxarifado["nome"])
    return True
