from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao


def selecionar_formacao(page: Page) -> bool:
    logger.info("Iniciou seleção comissão de inventário.")

    ctx = escopo(page)
    ha_resultado = selecionar_movimentacao(ctx, "COMISSAO DE INVENTARIO")

    if not ha_resultado:
        logger.info("Não há registros de comissão de inventário. ")
        return False 

    logger.info("Finalizou seleção comissão de inventário.")
    return True
