from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, clicar_com_ajax


def selecionar_ultima_movimentacao(page: Page) -> bool:
    logger.info("Iniciou seleção de última movimentação .")

    ctx = escopo(page)

    linha = ctx.locator("table[name='paginationTable'] tbody tr")

    count = linha.count()

    if count == 0:
        logger.info("Nenhuma movimentação encontrada.")
        return False

    clicar_com_ajax(ctx, linha.first.locator("button[name='submitUse']"))
    aguardar_ajax_global(page)

    logger.info("Finalizou seleção de última movimentação.")
    return True
