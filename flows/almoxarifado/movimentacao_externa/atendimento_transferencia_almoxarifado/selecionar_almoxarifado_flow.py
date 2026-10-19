from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, select_tipo


def selecionar_almoxarifado(page: Page, almoxarifado: dict) -> None:
    logger.info("Iniciou seleção do almoxarifado '{}' para atendimento de transferência.", almoxarifado["nome"])

    ctx = escopo(page)
    aguardar_ajax_global(page)
    logger.info("Selecionando almoxarifado {}.", almoxarifado["nome"])
    select_tipo(ctx, "almoxarifado", almoxarifado["nome"])

    logger.info("Finalizou seleção do almoxarifado {} para atendimento de transferência.", almoxarifado["nome"])