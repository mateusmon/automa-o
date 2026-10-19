from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_endereco(page: Page, endereco: dict) -> None:
    """
    Abre a Consulta de Endereço e filtra por `model-3` (chave `nome`).
    Cenário A. Apenas filtra e dispara a busca — a seleção fica no flow seguinte.

    :param endereco: dict do blueprint (usa a chave `nome`).
    """
    logger.info("Iniciou consulta de Endereço '{}'.", endereco["nome"])

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)
    logger.info("Filtrando Endereço pelo Nome (model-3): '{}'.", endereco["nome"])
    ctx.locator("input[name='model-3']").fill(endereco["nome"])
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de Endereço '{}'.", endereco["nome"])
