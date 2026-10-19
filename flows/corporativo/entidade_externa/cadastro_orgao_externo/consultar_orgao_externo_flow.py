from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_orgao_externo(page: Page, orgao_externo: dict) -> None:
    """
    Abre a Consulta de Órgão Externo e filtra por `model-4` (chave `nome`).
    Cenário A. Apenas filtra e dispara a busca — a seleção fica no flow seguinte.

    :param orgao_externo: dict do blueprint (usa a chave `nome`).
    """
    logger.info("Iniciou consulta de Órgão Externo '{}'.", orgao_externo["nome"])

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)
    
    logger.info("Preenchendo Nome de Órgão Externo: '{}'.", orgao_externo["nome"]) 
    ctx.locator("input[name='model-4']").fill(orgao_externo["nome"])
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de Órgão Externo '{}'.", orgao_externo["nome"])
