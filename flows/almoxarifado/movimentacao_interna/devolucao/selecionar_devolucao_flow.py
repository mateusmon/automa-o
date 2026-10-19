from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao


def selecionar_devolucao(page: Page, almoxarifado: dict[str, str]) -> bool:
    logger.info("Iniciou seleção de devolução no almoxarifado '{}'.", almoxarifado["nome"])

    ctx = escopo(page)
    encontrou = selecionar_movimentacao(ctx, almoxarifado["nome"])

    if not encontrou:
        logger.info("Nenhuma devolução encontrada para o almoxarifado '{}'.", almoxarifado["nome"])
    else:
        logger.info("Encontrou devolução para o almoxarifado '{}'.", almoxarifado["nome"])

    logger.info("Finalizou seleção de devolução no almoxarifado '{}'.", almoxarifado["nome"])
    return encontrou
