from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro

def alterar_enderecamento(page: Page, quantidade: str) -> None:
    logger.info("Alterando endereçamento.")

    ctx = escopo(page)

    logger.info("Alterando quantidade para '{}'.", quantidade)
    ctx.locator("input[name='qtCapacidade-1-5']").dblclick()
    ctx.locator("input[name='qtCapacidade-1-5']").fill(quantidade)

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Endereçamento alterado.")