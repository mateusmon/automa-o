from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def preencher_dados_gerais(page: Page, almoxarifado: dict) -> None:
    logger.info("Iniciou preenchimento de dados gerais de cadastro de ressuprimento para almoxarifado '{}'.", almoxarifado["sigla"])

    ctx = escopo(page)
    _preencher(ctx, page, almoxarifado)

    logger.info("Finalizou preenchimento de dados gerais de cadastro de ressuprimento para almoxarifado '{}'.", almoxarifado["sigla"])


def _preencher(ctx, page: Page, almoxarifado: dict) -> None:
    sigla_almoxarifado = almoxarifado["sigla"]

    logger.info("Preenchendo sigla do almoxarifado '{}'.", sigla_almoxarifado)
    preencher_campo(ctx, 'input[name="almoxarifado"]', sigla_almoxarifado, "lookup-cdAlmoxarifado")
    aguardar_ajax_global(page)

    logger.info("Preenchendo prazo '90'.")
    ctx.locator("input[name='prazo']").fill("90")
    aguardar_ajax_global(page)