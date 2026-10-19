from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def selecionar_pedido(page: Page, ua: dict) -> bool:
    logger.info("Iniciou seleção de pedido para UA '{}'.", ua["nome"])

    ctx = escopo(page)

    tabela = ctx.locator("table[name='paginationTable']")

    try:
        (
            tabela.locator("tr", has=ctx.locator("td", has_text=ua["nome"]))
            .first.wait_for(state="visible", timeout=2_000)
         )
    except Exception:
        logger.info("Pedido não encontrado para UA '{}'.", ua["nome"])
        return False
    
    linha = tabela.locator("tr", has=ctx.locator("td", has_text=ua["nome"])).first
    
    linha.locator("button[name='submitUse']").click()
    aguardar_ajax_global(page)
    
    logger.info("Finalizou seleção de pedido para UA '{}'.", ua["nome"])
    return True
