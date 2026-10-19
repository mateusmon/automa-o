from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_pais(page: Page, pais: dict) -> None:
    """
    Abre a Consulta de País e filtra pelo Nome (`model-1`).
    Cenário A. Apenas filtra e dispara a busca — a seleção fica no flow seguinte.

    :param pais: dict do blueprint (usa a chave `nome`).
    """
    logger.info("Iniciou consulta de País '{}'.", pais["nome"])

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)
    logger.info("Filtrando País pelo Nome: '{}'.", pais["nome"])
    ctx.locator("input[name='model-1']").fill(pais["nome"])
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de País '{}'.", pais["nome"])
