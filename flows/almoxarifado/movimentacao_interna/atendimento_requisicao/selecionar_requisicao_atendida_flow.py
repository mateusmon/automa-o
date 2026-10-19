from loguru import logger
from playwright.sync_api import Page

from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao
from utils.versao import escopo


def selecionar_requisicao_atendida(page: Page, ur: dict) -> bool:
    logger.info("Iniciou seleção de atendimento de requisição na UR '{}'.", ur["nome"])

    ctx = escopo(page)
    logger.info("Consultando atendimento de requisição na UR '{}'.", ur["nome"])
    resultado = selecionar_movimentacao(ctx, ur["nome"])

    if resultado:
        logger.info("Finalizou seleção de atendimento de requisição na UR '{}'.", ur["nome"])
    else:
        logger.info("Nenhum atendimento encontrado para a UR '{}'.", ur["nome"])

    return resultado
