from playwright.sync_api import Page
from loguru import logger

from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao
from utils.versao import escopo


def selecionar_requisicao(page: Page, ul: dict[str, str]) -> bool:
    logger.info("Iniciou seleção de requisições com a UL: '{}'.", ul["sigla"])

    ctx = escopo(page)

    ha_requisicoes = selecionar_movimentacao(ctx, ul["sigla"], "table[name='paginationTable'] tbody tr", "last")
    
    if ha_requisicoes:
        logger.info("Finalizou seleção de requisições com a UL: '{}'.", ul["sigla"])
        return True

    logger.info("Não há requisições feitas pela UL '{}'.", ul["sigla"])
    return ha_requisicoes
