from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo


def selecionar_recebimento(page: Page, almoxarifado: dict[str, str]) -> bool:
    logger.info("Iniciou seleção de recebimento de requisição no almoxarifado '{}'.", almoxarifado["nome"])

    ctx = escopo(page)
    
    if ctx.locator("table.tabela tbody tr").count() == 0:
        logger.info("Nenhum recebimento encontrado para o Almoxarifado '{}'.", almoxarifado["sigla"])
        return False

    logger.info("Foi encontrado um recebimento de requisição para o Almoxarifado '{}'.", almoxarifado["sigla"])

    logger.info("Finalizou seleção de recebimento de requisição no almoxarifado '{}'.", almoxarifado["nome"])
    return True
