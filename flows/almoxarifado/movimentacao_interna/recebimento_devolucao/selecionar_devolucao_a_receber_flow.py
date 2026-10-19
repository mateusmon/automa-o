from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo


def selecionar_devolucao(page: Page, almoxarifado: dict[str, str]) -> bool:
    logger.info("Iniciou seleção de devolução no almoxarifado: {}.", almoxarifado["nome"])

    ctx = escopo(page)

    linha = ctx.locator("table.tabela tbody tr").filter(has=ctx.locator("td").nth(3).filter(has_text=almoxarifado["nome"])).first

    if linha.count() == 0:
        logger.info("Nenhuma devolução com recebimento pendente encontrada para o almoxarifado '{}'.", almoxarifado["nome"])
        return False
    
    logger.info("Foi encontrada uma devolução com recebimento pendente para o almoxarifado '{}'.", almoxarifado["nome"])
    logger.info("Finalizou seleção de devolução no almoxarifado '{}'.", almoxarifado["nome"])
    return True
