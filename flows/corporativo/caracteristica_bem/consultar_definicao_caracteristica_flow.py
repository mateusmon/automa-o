from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_definicao_caracteristica(page: Page, caracteristica: dict) -> None:
    """
    Abre a Consulta da Definição da Característica e filtra pelo Nome (`model-1`).
    Cenário A. Apenas filtra e dispara a busca — a seleção fica no flow seguinte.

    Filtros confirmados ao vivo: model-0 Código (faixa), **model-1 Nome**, model-2 (lookup),
    model-3 (radio Tabelado), model-4 (faixa).

    :param caracteristica: dict do blueprint (usa a chave `nome`).
    """
    logger.info("Iniciou consulta da Definição da Característica '{}'.", caracteristica["nome"])

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Preenchendo Nome da Característica: '{}'.", caracteristica["nome"])
    ctx.locator("input[name='model-1']").fill(caracteristica["nome"])
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta da Definição da Característica '{}'.", caracteristica["nome"])
    
