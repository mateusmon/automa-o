from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import preencher_campo


def preencher_almoxarifado_solicitante(page: Page, almoxarifado: dict) -> None:
    logger.info("Iniciou preenchimento de almoxarifado solicitante '{}'.", almoxarifado["nome"])

    ctx = escopo(page)
    logger.info("Preenchendo sigla do almoxarifado solicitante: '{}'.", almoxarifado["sigla"])
    preencher_campo(ctx, "input[name='almoxarifadoDestino']", almoxarifado["sigla"])

    logger.info("Finalizou preenchimento de almoxarifado solicitante '{}'.", almoxarifado["nome"])
