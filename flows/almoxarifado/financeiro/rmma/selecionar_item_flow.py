from loguru import logger
from playwright.sync_api import Page, expect

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def selecionar_item(page: Page) -> bool:
    logger.info("Iniciou seleção de item para impressão de RMMA.")

    ctx = escopo(page)

    linhas = ctx.locator("table[name='paginationTable'] tbody tr")

    if linhas.count() < 1:
        logger.info("Nenhum item encontrado para seleção.")
        return False

    linhas.first.locator("button[name^='submitPrint']").click()
    aguardar_ajax_global(page)

    expect(ctx.locator("body")).to_contain_text("Relatório")

    logger.info("Finalizou seleção de item para impressão de RMMA.")
    return True
