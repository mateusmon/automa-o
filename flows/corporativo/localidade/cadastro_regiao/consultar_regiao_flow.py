from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_regiao(page: Page, regiao: dict) -> None:
    """
    Abre a Consulta de Região e filtra por `model-1` (chave `nome`).
    Cenário A. Apenas filtra e dispara a busca — a seleção fica no flow seguinte.

    :param regiao: dict do blueprint (usa a chave `nome`).
    """
    logger.info("Iniciou consulta de Região '{}'.", regiao["nome"])

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)
    logger.info("Filtrando Região pelo campo de Nome: '{}'.", regiao["nome"])
    ctx.locator("input[name='model-1']").fill(regiao["nome"])
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de Região '{}'.", regiao["nome"])
