from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_ua(page: Page, unidade_administrativa: dict) -> None:
    """
    Abre a Consulta de UA - Unidade Administrativa e filtra por `model-4` (chave `sigla`).
    Cenário A. Apenas filtra e dispara a busca — a seleção fica no flow seguinte.

    :param unidade_administrativa: dict do blueprint (usa a chave `sigla`).
    """
    logger.info("Iniciou consulta de UA - Unidade Administrativa: '{}'.", unidade_administrativa["sigla"])

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)
    logger.info("Filtrando UA - Unidade Administrativa pelo campo de Sigla: '{}'.", unidade_administrativa["sigla"])
    ctx.locator("input[name='model-4']").fill(unidade_administrativa["sigla"])
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de UA - Unidade Administrativa: '{}'.", unidade_administrativa["sigla"])
