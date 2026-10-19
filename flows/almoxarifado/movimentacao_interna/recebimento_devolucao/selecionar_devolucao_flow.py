from loguru import logger
from playwright.sync_api import Page

from utils.waits import aguardar_ajax_global
from utils.versao import escopo


def selecionar_devolucao(page: Page, almoxarifado: dict[str, str]) -> bool:
    logger.info("Iniciou seleção de recebimento de devolução de materiais no almoxarifado '{}'.", almoxarifado["nome"])

    ctx = escopo(page)

    linha = ctx.locator("table[name='paginationTable'] tbody tr").filter(has=ctx.locator("td").nth(0).filter(has_text=almoxarifado["nome"])).first

    if linha.count() == 0:
        logger.info("Não foi encontrado nenhum recebimento de devolução do almoxarifado '{}'.", almoxarifado["nome"])
        return False

    logger.info("Foi encontrado um recebimento de devolução do almoxarifado '{}'.", almoxarifado["nome"])

    linha.locator("button[name='submitUse']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou seleção de recebimento de devolução de materiais no almoxarifado '{}'.", almoxarifado["nome"])
    return True
