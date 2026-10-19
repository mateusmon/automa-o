from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_almoxarifado(page: Page, almoxarifado: dict) -> None:
    """
    Abre a Consulta de Almoxarifado e filtra por `model-4` (chave `sigla`).
    Cenário A. Apenas filtra e dispara a busca — a seleção fica no flow seguinte.

    :param almoxarifado: dict do blueprint (usa a chave `sigla`).
    """
    logger.info("Iniciou consulta de Almoxarifado ' {}'.", almoxarifado["sigla"])

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Preenchendo Sigla de Almoxarifado: '{}'.", almoxarifado["sigla"])
    ctx.locator("input[name='model-4']").fill(almoxarifado["sigla"])
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de Almoxarifado ' {}'.", almoxarifado["sigla"])
