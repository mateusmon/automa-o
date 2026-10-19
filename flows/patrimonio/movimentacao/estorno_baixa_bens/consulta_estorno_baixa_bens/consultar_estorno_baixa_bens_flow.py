import re

from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global

def consultar_estorno_baixa_bens(page: Page, ug: dict[str, str]) -> bool:
    logger.info("Consultando estorno da baixa de bens.")

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    # Preenche UG
    ctx.locator("input[name='model-2']").fill(ug["codigo"])
    ctx.locator("button[name='lookup-model-2']").click()

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    linha = ctx.locator("table[name='paginationTable'] tbody tr").filter(
        has=ctx.locator("td").nth(0).filter(
            has_text=ug["nome"]
        )
    ).filter(
        has=ctx.locator("td").nth(4).filter(
            has_text=re.compile(r"\S")
        )
    ).first

    if linha.count() == 0:
        logger.info("Nenhum estorno de baixa encontrado.")
        return False
    
    linha.locator("button[name='submitUse']").click()
    aguardar_ajax_global(page)

    logger.info("Estorno de baixa de bens consultado.")

    return True