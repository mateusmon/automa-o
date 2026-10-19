from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_fornecedor(page: Page, fornecedor: dict) -> None:
    """
    Abre a Consulta de Fornecedor e filtra por CNPJ (`model-2`, formatado).
    Cenário A. Apenas filtra e dispara a busca — a seleção fica no flow seguinte.

    :param fornecedor: dict do blueprint (usa a chave `cnpj`).
    """
    logger.info("Iniciou consulta de Fornecedor '{}'.", fornecedor["nome"])

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    _v = fornecedor["cnpj"]
    valor = f"{_v[:2]}.{_v[2:5]}.{_v[5:8]}/{_v[8:12]}-{_v[12:]}"
    logger.info("Preenchendo CNPJ de Fornecedor: '{}'.", valor)
    ctx.locator("input[name='model-2']").fill(valor)
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de Fornecedor '{}'.", fornecedor["nome"])
