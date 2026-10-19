from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_ur(page: Page, unidade_requisicao: dict) -> None:
    """
    Abre a Consulta de UR - Unidade de Requisição e filtra por `model-5` (chave `nome`).
    Cenário A. Apenas filtra e dispara a busca — a seleção fica no flow seguinte.

    :param unidade_requisicao: dict do blueprint (usa a chave `nome`).
    """
    logger.info("Iniciou consulta de UR - Unidade de Requisição: '{}'.", unidade_requisicao["nome"])

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)
    logger.info("Filtrando UR - Unidade de Requisição pelo Nome: '{}'.", unidade_requisicao["nome"])
    ctx.locator("input[name='model-5']").fill(unidade_requisicao["nome"])
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de UR - Unidade de Requisição: '{}'.", unidade_requisicao["nome"])
