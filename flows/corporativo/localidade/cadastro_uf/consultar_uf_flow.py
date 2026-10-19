from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_uf(page: Page, uf: dict) -> None:
    """
    Abre a Consulta de UF - Unidade da Federação e filtra por `model-1` (chave `nome`).
    Cenário A. Apenas filtra e dispara a busca — a seleção fica no flow seguinte.

    :param uf: dict do blueprint (usa a chave `nome`).
    """
    logger.info("Iniciou consulta de UF - Unidade da Federação '{}'.", uf["nome"])

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)
    logger.info("Filtrando UF - Unidade da Federação pelo campo de Nome: '{}'.", uf["nome"])
    ctx.locator("input[name='model-1']").fill(uf["nome"])
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de UF - Unidade da Federação '{}'.", uf["nome"])
