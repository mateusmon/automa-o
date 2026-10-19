from playwright.sync_api import Page, expect
from loguru import logger

from utils.versao import escopo
from utils.waits import preencher_campo


def preencher_almoxarifado(page: Page, almoxarifado: dict[str, str]) -> None:
    """
    Preenche o campo Almoxarifado nos dados gerais da entrada e aguarda os
    campos dependentes (ex.: UG) serem preenchidos automaticamente.

    Parâmetros:
        page (Page): Instância da página do Playwright.
        almoxarifado (dict[str, str]): Dados do almoxarifado (usa a chave 'sigla').
    """
    logger.info("Iniciou preenchimento do almoxarifado '{}'.", almoxarifado["nome"])

    ctx = escopo(page)
    logger.info("Preenchendo sigla do almoxarifado: '{}'.", almoxarifado["sigla"])
    preencher_campo(ctx, "#almoxarifado", almoxarifado["sigla"])

    # Espera os demais campos serem preenchidos automaticamente.
    expect(ctx.locator('input[name="ug"]')).not_to_have_value("")

    logger.info("Finalizou preenchimento do almoxarifado '{}'.", almoxarifado["nome"])
