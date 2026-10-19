from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def selecionar_numero_patrimonial(page: Page, ug: dict[str, str]) -> bool:
    logger.info("Iniciou seleção de modificação do número patrimonial")

    ctx = escopo(page)

    linha = ctx.locator("table[name='paginationTable'] tbody tr").filter(
        has=ctx.locator("td").nth(1).filter(has_text=ug["nome"])
    ).first

    if linha.count() == 0:
        logger.info("Modificação de número patrimonial não encontrada para a U.G")
        return False

    linha.locator("button[name='submitUse']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou seleção de modificação do número patrimonial")
    return True
