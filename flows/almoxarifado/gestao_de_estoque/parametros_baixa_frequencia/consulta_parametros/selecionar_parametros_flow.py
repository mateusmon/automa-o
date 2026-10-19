from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo


def selecionar_parametros(page: Page) -> bool:
    logger.info("Iniciou seleção de parâmetros de baixa frequência.")

    ctx = escopo(page)

    linha = ctx.locator("table.tabela tbody tr").first

    if linha.count() == 0:
        logger.info("Nenhum material de baixa frequência encontrado.")
        return False

    logger.info("Finalizou seleção de parâmetros de baixa frequência.")
    return True
