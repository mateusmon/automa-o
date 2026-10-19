from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import clicar_com_ajax


def confirmar_modificacao(page: Page) -> None:
    logger.info("Iniciou confirmação da modificação do status de bem.")

    ctx = escopo(page)

    clicar_com_ajax(ctx, "button[name='submitFinish']")

    logger.info("Finalizou confirmação da modificação do status de bem.")