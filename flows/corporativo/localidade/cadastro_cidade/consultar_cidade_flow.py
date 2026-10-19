from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_cidade(page: Page, cidade: dict) -> None:
    """
    Abre a Consulta de Cidade e filtra por `model-1` (chave `nome`).
    Cenário A. Apenas filtra e dispara a busca — a seleção fica no flow seguinte.

    :param cidade: dict do blueprint (usa a chave `nome`).
    """
    logger.info("Iniciou consulta de Cidade '{}'.", cidade["nome"])

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)
    logger.info("Filtrando Cidade pelo Nome: '{}'.", cidade["nome"])
    ctx.locator("input[name='model-1']").fill(cidade["nome"])
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de Cidade '{}'.", cidade["nome"])
