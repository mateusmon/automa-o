from playwright.sync_api import Page
from loguru import logger

from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao
from utils.versao import escopo


def selecionar_situacao_fisica(page: Page, nome: str) -> bool:
    logger.info("Iniciou seleção de situação física: '{}'.", nome)

    ctx = escopo(page)

    encontrou = selecionar_movimentacao(ctx, nome)

    if not encontrou:
        logger.info("Nenhuma situação física com o nome '{}' encontrada.", nome)
        return False

    logger.info("Foi encontrada uma situação física com o nome '{}'.", nome)
    logger.info("Finalizou seleção de situação física: '{}'.", nome)
    return True
