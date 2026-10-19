from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_situacao_fisica(page: Page, nome: str) -> None:
    logger.info("Iniciou consulta de situação física: '{}'.", nome)

    ctx = escopo(page)

    ctx.click("button[name='submitSearch']")
    aguardar_ajax_global(page)

    logger.info("Preenchendo situação física: '{}'.", nome)
    ctx.fill("input[name='model-1']", nome)

    ctx.click("button[name='submitSearch']")
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de situação física: '{}'.", nome)
