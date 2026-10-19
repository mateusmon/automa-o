from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import select_tipo


def selecionar_status(page: Page, status: str) -> None:
    logger.info("Iniciou seleção de novo status de bem '{}'.", status)

    ctx = escopo(page)

    if not select_tipo(ctx, "cdStatusD", status):
        logger.info("Status de nome '{}' não encontrado.", status)

    logger.info("Finalizou seleção de novo status de bem {}.", status)
