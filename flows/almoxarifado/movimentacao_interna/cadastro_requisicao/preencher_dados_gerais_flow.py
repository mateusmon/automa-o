from playwright.sync_api import Page
from loguru import logger

from utils.waits import preencher_campo
from utils.versao import escopo


def preencher_dados_gerais(page: Page, ur: dict[str, str], almoxarifado: dict[str, str]) -> None:
    logger.info("Iniciou preenchimento de dados gerais no almoxarifado '{}'.", almoxarifado["nome"])

    ctx = escopo(page)
    _preencher(ctx, ur, almoxarifado)

    logger.info("Finalizou preenchimento de dados gerais no almoxarifado '{}'.", almoxarifado["nome"])


def _preencher(ctx, ur: dict[str, str], almoxarifado: dict[str, str]) -> None:
    # Código removido temporariamente. Se houver algum cliente que precise disso, descomente
    # if ctx.locator("input[name='ur']").input_value() == "":
    #     campo_ur.clear()

    logger.info("Preenchendo sigla da UR: '{}'.", ur["sigla_ua"])
    preencher_campo(ctx, "input[name='ur']", ur["nome"])
    logger.info("Preenchendo sigla do almoxarifado: '{}'.", almoxarifado["sigla"])
    preencher_campo(ctx, "input[name='almoxarifado']", almoxarifado["sigla"])
