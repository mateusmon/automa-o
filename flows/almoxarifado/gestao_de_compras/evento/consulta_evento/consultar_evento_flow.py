from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, clicar_com_ajax

def consultar_evento(page: Page, nome: str = "UM GRANDE EVENTO"):
    logger.info("Consultando evento {}.", nome)

    ctx = escopo(page)

    page.mouse.move(0, 0)

    clicar_com_ajax(ctx, "button[name='submitSearch']")
    clicar_com_ajax(ctx, "button[name='submitSearch']")

    linha = ctx.locator("table[name='paginationTable'] tbody tr").filter(has_text=nome).last

    if linha.count() == 0:
        logger.info("Evento {} não encontrado.", nome)
        return False
    
    linha.locator("button[name='submitUse']").click()

    aguardar_ajax_global(page)

    logger.info("Evento '{}' consultado.", nome)
    
    return True