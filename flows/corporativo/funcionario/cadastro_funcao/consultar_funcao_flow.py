from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_funcao(page: Page, funcao: dict) -> None:
    """
    Abre a Consulta de Função e filtra por `model-1` (chave `nome`).
    Cenário A. Apenas filtra e dispara a busca — a seleção fica no flow seguinte.

    :param funcao: dict do blueprint (usa a chave `nome`).
    """
    logger.info("Iniciou consulta de Função '{}'.", funcao["nome"])

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)
    
    logger.info("Filtrando Função pelo Nome: '{}'.", funcao["nome"])
    ctx.locator("input[name='model-1']").fill(funcao["nome"])
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de Função '{}'.", funcao["nome"])
