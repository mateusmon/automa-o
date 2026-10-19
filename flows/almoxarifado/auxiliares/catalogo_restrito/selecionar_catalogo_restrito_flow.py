from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao


def selecionar_catalogo_restrito(page: Page, nome_catalogo: str) -> bool:
    logger.info("Iniciou seleção de catálogo restrito '{}'.", nome_catalogo)

    ctx = escopo(page)

    if not selecionar_movimentacao(ctx, nome_catalogo, "table[name='paginationTable'] tbody tr", "last"):
        logger.info("Catálogo restrito '{}' não encontrado.", nome_catalogo)    
        return False

    logger.info("Finalizou seleção de catálogo restrito '{}'.", nome_catalogo)
    return True
