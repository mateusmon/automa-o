from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def consultar_parametros(page: Page, almoxarifado: dict) -> None:
    logger.info("Iniciou consulta de parâmetros de baixa frequência do almoxarifado '{}'.", almoxarifado["sigla"])

    ctx = escopo(page)

    logger.info("Preenchendo sigla do almoxarifado: '{}'.", almoxarifado["sigla"])
    preencher_campo(ctx, "input[name='cdAlmoxarifado']", almoxarifado["sigla"])
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de parâmetros de baixa frequência.")
