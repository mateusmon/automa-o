from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def selecionar_modificacao(page: Page, ua: dict[str, str]) -> bool:
    logger.info("Iniciou seleção de modificação de responsável local.")

    ctx = escopo(page)

    linha = ctx.locator("table[name='paginationTable'] tbody tr").filter(
        has=ctx.locator("td").nth(2).filter(has_text=ua["nome"])
    ).first

    if linha.count() == 0:
        logger.info("Nenhuma modificação de responsável local encontrada para a U.A. '{}'.", ua["nome"])
        return False

    linha.locator("button[name='submitUse']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou seleção de modificação de responsável local.")
    return True
