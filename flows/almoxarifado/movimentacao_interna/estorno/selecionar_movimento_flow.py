from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao


def selecionar_movimento(page: Page, almoxarifado: dict) -> bool:
    logger.info("Iniciou seleção de movimento no almoxarifado: {}.", almoxarifado["nome"])

    ctx = escopo(page)
    existe_movimento = selecionar_movimentacao(ctx, almoxarifado["nome"])

    if not existe_movimento:
        logger.info("Nenhuma nota de recebimento encontrada para almoxarifado '{}'.", almoxarifado["nome"])
        return False

    logger.info("Foi encontrada uma nota de recebimento para almoxarifado '{}'.", almoxarifado["nome"])
    logger.info("Finalizou seleção de movimento no almoxarifado: {}.", almoxarifado["nome"])
    return True
