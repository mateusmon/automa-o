from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import select_tipo


def selecionar_almoxarifado(page: Page, almoxarifado: dict[str, str]) -> None:
    logger.info("Iniciou seleção do almoxarifado: {}.", almoxarifado["nome"])

    logger.info("Selecionando almoxarifado: {}.", almoxarifado["nome"])
    select_tipo(escopo(page), "almoxarifado", almoxarifado["nome"])

    logger.info("Finalizou seleção do almoxarifado: {}.", almoxarifado["nome"])
