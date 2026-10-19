from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao


def selecionar_estorno(page: Page, funcionario: dict[str, str]) -> bool:
    logger.info("Iniciou seleção de estorno de material para o funcionário: {}.", funcionario["nome"])

    ctx = escopo(page)

    existe_estorno = selecionar_movimentacao(ctx, funcionario["nome"])

    if not existe_estorno:
        logger.info("Não foi encontrado nenhum estorno do material para o funcionário: {}.", funcionario["nome"])
    else:
        logger.info("Foi encontrado um estorno do material para o funcionário: {}.", funcionario["nome"])

    logger.info("Finalizou seleção de estorno de material para o funcionário: {}.", funcionario["nome"])
    return existe_estorno
