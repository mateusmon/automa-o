from playwright.sync_api import Page
from loguru import logger

from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao
from utils.versao import escopo


def selecionar_catalogo(page: Page, ug: dict[str, str]) -> bool:
    logger.info("Iniciou seleção de Catálogo de Materiais na UG '{}'.", ug["nome"])

    ctx = escopo(page)

    encontrou = selecionar_movimentacao(ctx, ug["nome"], posicao="last")

    if not encontrou:
        logger.info("Nenhum catálogo encontrado na UG '{}'.", ug["nome"])
        return False

    logger.info("Foi encontrado um catálogo na UG '{}'.", ug["nome"])
    logger.info("Finalizou seleção de Catálogo de Materiais na UG '{}'.", ug["nome"])
    return True
