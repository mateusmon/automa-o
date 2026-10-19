from playwright.sync_api import Page, expect
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_conta(page: Page) -> None:
    logger.info("Iniciou consulta de conta contábil.")

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)
    
    primeira_linha = ctx.locator("table[name='paginationTable'] tbody tr").first
    primeira_linha.locator("button[name='submitUse']").click()
    aguardar_ajax_global(page)

    expect(page.get_by_role("heading", name="Conta Contábil")).to_be_visible()

    logger.info("Finalizou consulta de conta contábil.")
