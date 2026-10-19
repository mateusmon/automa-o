from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_ug(page: Page, ug: dict) -> None:
    """
    Abre a Consulta de UG - Unidade Gestora e filtra por `model-2` (chave `nome`).
    Cenário A. Apenas filtra e dispara a busca — a seleção fica no flow seguinte.

    :param ug: dict do blueprint (usa a chave `nome`).
    """
    logger.info("Iniciou consulta de UG - Unidade Gestora: '{}'.", ug["codigo"])

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Filtrando UG - Unidade Gestora pelo Nome: '{}'.", ug["nome"])
    ctx.locator("input[name='model-2']").fill(ug["nome"])
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de UG - Unidade Gestora: '{}'.", ug["codigo"])
