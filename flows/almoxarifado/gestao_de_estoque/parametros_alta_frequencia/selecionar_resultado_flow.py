from playwright.sync_api import Page
from loguru import logger

from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao
from utils.versao import escopo


def selecionar_resultado(page: Page, almoxarifado: dict[str, str]) -> bool:
    logger.info("Iniciou seleção de movimentação no almoxarifado '{}'.", almoxarifado["sigla"])

    ctx = escopo(page)

    if not selecionar_movimentacao(ctx, almoxarifado["nome"]):
        logger.info("Nenhuma movimentação encontrada para '{}'.", almoxarifado["nome"])
        return False
    
    logger.info("Finalizou seleção de movimentação no almoxarifado '{}'.", almoxarifado["sigla"])
    return True
