from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_modelo_importacao(page: Page, modelo: dict) -> None:
    """
    Abre a Consulta do Modelo de Importação e filtra pela Descrição (`model-1`, chave).
    Cenário A. Apenas filtra e dispara a busca — a seleção fica no flow seguinte.

    :param modelo: dict do blueprint (usa a chave `descricao`).
    """
    logger.info("Iniciou consulta de Modelo de Importação.")

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    ctx.locator("input[name='model-1']").fill(modelo["descricao"])
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de Modelo de Importação.")
