from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_caracteristicas(page: Page) -> None:
    """
    Abre o lookup de característica do Modelo de Importação e dispara a consulta sem
    filtro. Cenário A. A seleção/anexação fica no flow seguinte.

    O grid de Características exige ao menos uma característica; a consulta lista as
    disponíveis para o bem selecionado (o catálogo varia por cliente).
    """
    logger.info("Iniciou consulta de características.")

    ctx = escopo(page)

    ctx.locator("button[name='lookup-caracteristica-1-3']").click()
    aguardar_ajax_global(page)
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de características.")
