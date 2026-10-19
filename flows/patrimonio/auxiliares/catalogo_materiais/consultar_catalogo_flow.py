from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_catalogo(page: Page, ug: dict[str, str]) -> None:
    logger.info("Iniciou consulta de Catálogo de Materiais na UG '{}'.", ug["nome"])

    ctx = escopo(page)

    ctx.click("button[name='submitSearch']")
    aguardar_ajax_global(page)

    logger.info("Preenchendo código da UG: '{}'.", ug["codigo"])
    ctx.fill("input[name='model-1']", ug["codigo"])
    ctx.click("button[name='lookup-model-1']")
    aguardar_ajax_global(page)

    ctx.click("button[name='submitSearch']")
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de Catálogo de Materiais na UG '{}'.", ug["nome"])
