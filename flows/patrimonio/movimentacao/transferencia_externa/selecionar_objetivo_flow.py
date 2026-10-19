from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, select_tipo


def selecionar_objetivo(page: Page, objetivo: str) -> None:
    logger.info("Iniciou seleção do objetivo: '{}'.", objetivo)

    ctx = escopo(page)

    select_tipo(ctx, "motivoSaidaTemp", objetivo)
    aguardar_ajax_global(page)

    logger.info("Finalizou seleção do objetivo: '{}'.", objetivo)