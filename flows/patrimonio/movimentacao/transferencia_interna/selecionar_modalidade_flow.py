from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import select_tipo


def selecionar_modalidade(page: Page, modalidade: str) -> bool:
    logger.info("Iniciou seleção de modalidade: '{}'.", modalidade)

    ctx = escopo(page)

    resultado = select_tipo(ctx, "modoTransferencia", modalidade)

    logger.info("Finalizou seleção de modalidade: '{}'.", modalidade)
    return resultado
