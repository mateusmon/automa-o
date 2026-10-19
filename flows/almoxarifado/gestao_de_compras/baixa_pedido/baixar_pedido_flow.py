from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def baixar_pedido(page: Page) -> None:
    logger.info("Iniciou seleção de pedido.")

    ctx = escopo(page)

    logger.info("Preenchendo quantidade a baixar '0'.")
    ctx.locator("input[name='qtABaixar-1-6']").fill("0")
    ctx.locator("input[name='baixarItem-1-7']").check()
    
    logger.info("Finalizou seleção de pedido.")
    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)
