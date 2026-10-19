from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_ul(page: Page, ul: dict) -> None:
    """
    Abre a Consulta de UL - Unidade de Localização e filtra pela Sigla (`model-8`).
    Cenário A. Apenas filtra e dispara a busca — a seleção fica no flow seguinte.

    A UL não tem campo Nome; a Sigla (`sgUl`) é o identificador de texto livre.
    Filtros confirmados ao vivo: model-0 Órgão, model-1 U.G., model-2 U.A., model-3 C.C.,
    model-4 Código (faixa), model-5 Nome, model-6 Conta, model-7 Endereço, **model-8 Sigla**.

    :param ul: dict do blueprint (usa a chave `sigla`).
    """
    logger.info("Iniciou consulta de UL - Unidade de Localização: '{}'.", ul["sigla"])

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)
    logger.info("Filtrando UL - Unidade de Localização pelo campo de Sigla: '{}'.", ul["sigla"])
    ctx.locator("input[name='model-8']").fill(ul["sigla"])
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de UL - Unidade de Localização: '{}'.", ul["sigla"])
