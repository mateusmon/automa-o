from playwright.sync_api import Page
from loguru import logger

from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao
from utils.versao import escopo


def selecionar_endereco(page: Page, endereco: str) -> bool:
    logger.info("Iniciou seleção do endereço de estoque '{}'.", endereco)

    ctx = escopo(page)

    if not selecionar_movimentacao(ctx, endereco):
        logger.info("Nenhum endereço de estoque encontrado com nome '{}'.", endereco,)
        return False

    logger.info("Finalizou seleção de endereço de estoque '{}'.", endereco)
    return True
