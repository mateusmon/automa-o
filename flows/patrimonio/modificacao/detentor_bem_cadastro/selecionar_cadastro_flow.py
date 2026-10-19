from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao


def selecionar_cadastro(page: Page, funcionario: dict[str, str]) -> bool:
    logger.info("Iniciou seleção de cadastro de detentor do bem {}.", funcionario["nome"])

    ctx = escopo(page)
    encontrou = selecionar_movimentacao(ctx, funcionario["nome"])

    if not encontrou:
        logger.info("Nenhum cadastro de detentor do bem encontrado para '{}'.", funcionario["nome"])
        return False

    logger.info("Finalizou seleção de cadastro de detentor do bem {}.", funcionario["nome"])
    return True
