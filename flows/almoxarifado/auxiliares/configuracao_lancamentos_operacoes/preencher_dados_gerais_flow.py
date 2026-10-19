from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo

def preencher_dados_gerais(page: Page) -> None:
    logger.info("Preenchendo dados gerais.")

    ctx = escopo(page)

    logger.info("Preenchendo sigla 'ATMO'.")
    ctx.locator("input[name='sgTipoMovimento']").fill("ATMO")

    if ctx.locator("input[name='dsTipoMovimento']").is_visible():
        logger.info("Preenchendo nome 'AUTOMAÇÃO'.")
        ctx.locator("input[name='dsTipoMovimento']").fill("AUTOMAÇÃO")

    logger.info("Preenchimento de dados gerais finalizado.")
