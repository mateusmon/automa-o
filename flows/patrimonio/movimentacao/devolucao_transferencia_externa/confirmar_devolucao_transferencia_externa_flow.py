from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import clicar_com_ajax


def confirmar_devolucao_transferencia_externa(page: Page) -> None:
    logger.info("Iniciou a confirmação da devolução de transferência externa.")

    ctx = escopo(page)

    logger.info("Clicando botão 'Confirmar'.")
    clicar_com_ajax(ctx, "button[name='submitFinish']")

    logger.info("Finalizou a confirmação da devolução de transferência externa.")