from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def desfazer_movimento(page: Page) -> None:
    ctx = escopo(page)
    logger.info("Iniciou desfazimento de movimento '{}'.", ctx.locator("input[name='bens-1-7']").input_value())

    ctx.locator("input[name='bens-1-7']").dblclick()
    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou desfazimento de movimento '{}'.", ctx.locator("input[name='bens-1-7']").input_value())
