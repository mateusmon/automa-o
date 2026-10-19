from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, clicar_com_ajax

def alterar_documento(page: Page):
    logger.info("Alterando documento.")

    ctx = escopo(page)

    # Clica para bloquear ou para desbloquear
    clicar_com_ajax(ctx, "input[name='bloqueado']")

    clicar_com_ajax(ctx, "button[name='submitFinish']")
    aguardar_ajax_global(page)

    logger.info("Documento alterado.")