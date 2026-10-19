from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao


def selecionar_modificacao(page: Page, ug_data: dict[str, str])-> bool:
    logger.info("Iniciou seleção de modificação de status de bem {}.", ug_data["nome"])

    ctx = escopo(page)
    achou_bem = selecionar_movimentacao(ctx, ug_data["nome"])

    if not achou_bem:
        logger.info("Nenhuma modificação de status encontrada para seleção {}.", ug_data["nome"])
        return False

    logger.info("Finalizou seleção de modificação de status de bem {}.", ug_data["nome"])
    return True
