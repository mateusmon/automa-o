from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao


def selecionar_requisicao(page: Page, ur: dict) -> bool:
    logger.info("Iniciou seleção de requisição na UR '{}'.", ur["nome"])

    ctx = escopo(page)
    existe_requisicao = selecionar_movimentacao(ctx, ur["nome"])

    if not existe_requisicao:
        logger.info("Nenhuma requisição encontrada para '{}'.", ur["nome"])
    else:
        logger.info("Encontrou requisição para a UR '{}'.", ur["nome"])

    logger.info("Finalizou seleção de requisição na UR '{}'.", ur["nome"])
    return existe_requisicao
