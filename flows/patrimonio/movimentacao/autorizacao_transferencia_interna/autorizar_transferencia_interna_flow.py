from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro

def autorizar_transferencia_interna(page: Page) -> None:
    logger.info("Autorizando Transferência Interna.")

    ctx = escopo(page)

    ctx.locator("input[name='transferenciaAutorizadaSim']").click()
    aguardar_ajax_global(page)
    
    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Transferência Interna autorizada com sucesso.")