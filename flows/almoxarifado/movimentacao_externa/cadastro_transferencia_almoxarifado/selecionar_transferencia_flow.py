from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao


def selecionar_transferencia(page: Page, almoxarifado: dict[str, str]) -> bool:
    logger.info("Iniciou seleção de cadastro de transferência entre almoxarifados.")

    ctx = escopo(page)
    logger.info("Selecionando almoxarifado '{}'.", almoxarifado["nome"])
    encontrou = selecionar_movimentacao(ctx, almoxarifado["nome"])

    if not encontrou:
        logger.info("Nenhum cadastro de transferência entre almoxarifados encontrado para o almoxarifado '{}'.", almoxarifado["nome"])
        return False

    logger.info("Finalizou seleção de cadastro de transferência entre almoxarifados.")
    return True
