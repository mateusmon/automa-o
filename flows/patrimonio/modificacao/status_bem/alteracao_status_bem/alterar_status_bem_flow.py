from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def alterar_status_bem(page: Page, motivo: str = "Não Localizado") -> None:
    ctx = escopo(page)
    logger.info("Iniciou alteração de status do bem.")

    logger.info("Alterando status do bem para '{}'.", motivo)
    ctx.locator("input[name='bens-1-7']").fill(motivo)
    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou alteração de status do bem.")
