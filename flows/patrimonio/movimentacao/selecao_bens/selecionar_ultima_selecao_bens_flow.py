from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def selecionar_ultima_selecao_bens(page: Page) -> bool:
    logger.info("Iniciou seleção de última seleção de bens.")

    ctx = escopo(page)

    ctx.locator("table[name='paginationTable'] tbody").wait_for(state="visible")

    linha = ctx.locator("table[name='paginationTable'] tbody tr")

    count = linha.count()

    if count == 0:
        logger.info("Nenhuma Seleção de Bens encontrada.")
        return False

    linha.last.locator("button[name='submitUse']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou seleção de última de seleção de bens.")
    return True
