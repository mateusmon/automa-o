from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_portador(page: Page, portador: dict) -> None:
    """
    Abre a Consulta de Portador e filtra por CPF (`model-2`, formatado).
    Cenário A. Apenas filtra e dispara a busca — a seleção fica no flow seguinte.

    :param portador: dict do blueprint (usa a chave `cpf`).
    """
    logger.info("Iniciou consulta de Portador '{}'.", portador["nome"])

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    _v = portador["cpf"]
    valor = f"{_v[:3]}.{_v[3:6]}.{_v[6:9]}-{_v[9:]}"
    logger.info("Preenchendo CPF de Portador: '{}'.", valor)
    ctx.locator("input[name='model-2']").fill(valor)
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de Portador '{}'.", portador["nome"])
