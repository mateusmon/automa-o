from playwright.sync_api import Page
from loguru import logger

from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao


def selecionar_transferencia(page: Page, almoxarifado: dict[str, str]) -> bool:
    logger.info("Iniciou seleção de transferência para atendimento no almoxarifado {}.", almoxarifado["nome"])

    encontrou = selecionar_movimentacao(page, almoxarifado["nome"])
    if not encontrou:
        logger.info("Nenhuma transferência encontrada para o almoxarifado {}.", almoxarifado["nome"])

    logger.info("Finalizou seleção de transferência para atendimento no almoxarifado {}.", almoxarifado["nome"])
    return encontrou
