from playwright.sync_api import Page
from loguru import logger

from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao
from utils.versao import escopo


def selecionar_roteiro_padrao_baixa(page: Page) -> bool:
    logger.info("Iniciou seleção de Roteiro Padrão para Baixa.")

    ctx = escopo(page)

    encontrou = selecionar_movimentacao(ctx, "ROTEIRO DE BAIXA")

    if not encontrou:
        logger.info("Nenhum Roteiro Padrão para Baixa 'ROTEIRO DE BAIXA' encontrado.")
        return False

    logger.info("Foi encontrado um Roteiro Padrão para Baixa 'ROTEIRO DE BAIXA'.")
    logger.info("Finalizou seleção de Roteiro Padrão para Baixa.")
    return True
