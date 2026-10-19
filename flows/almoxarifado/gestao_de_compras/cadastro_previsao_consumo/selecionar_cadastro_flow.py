from playwright.sync_api import Page
from loguru import logger

from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao
from utils.versao import escopo


def selecionar_cadastro(page: Page, ur_data: dict[str, str]) -> bool:
    logger.info("Iniciou seleção de cadastro de previsão de consumo da UR '{}'.", ur_data["nome"])

    ctx = escopo(page)

    if not selecionar_movimentacao(ctx, ur_data["nome"]):
        logger.info("Não há cadastros de previsão a serem selecionados para UR '{}'.", ur_data["nome"])
        return False

    logger.info("Finalizou seleção de cadastro de previsão de consumo da UR '{}'.", ur_data["nome"])
    return True
