from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_cc(page: Page, centro_custo: dict) -> None:
    """
    Abre a Consulta de CC - Centro de Custos e filtra pelo Nome (`model-2`, chave).
    Cenário A. Apenas filtra e dispara a busca — a seleção fica no flow seguinte.

    :param centro_custo: dict do blueprint (usa a chave `nome`).
    """
    logger.info("Iniciou consulta de CC - Centro de Custos '{}'.", centro_custo["nome"])

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Filtrando CC - Centro de Custos pelo Nome: '{}'.", centro_custo["nome"])
    logger.debug("Preenchendo campo de Nome do CC - Centro de Custos (model-2) com '{}'.", centro_custo["nome"])
    ctx.locator("input[name='model-2']").fill(centro_custo["nome"])
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de CC - Centro de Custos. Filtrado pelo Nome: '{}'.", centro_custo["nome"])
