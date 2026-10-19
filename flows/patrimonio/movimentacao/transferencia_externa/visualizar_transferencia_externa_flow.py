from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, clicar_com_ajax


def visualizar_transferencia_externa(page: Page) -> None:
    logger.info("Iniciou a visualização da Transferência Externa.")

    ctx = escopo(page)

    clicar_com_ajax(ctx, ctx.locator("button[name='submitView']"))
    aguardar_ajax_global(page)
    clicar_com_ajax(ctx, ctx.locator("button[name='submitBack']"))
    aguardar_ajax_global(page)

    logger.info("Finalizou a visualização da Transferência Externa.")