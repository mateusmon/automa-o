from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import preencher_campo

def preencher_etiquetas(page: Page, ug: dict[str, str], num_patrimonial: str):
    logger.info("Preenchendo seção das etiquetas.")

    ctx = escopo(page)

    # Preenche U.G.
    preencher_campo(ctx, "input[name='ug']", ug["codigo"])

    # Preenche número patrimonial
    logger.info("Preenchendo número patrimonial: '{}'.", num_patrimonial)
    ctx.locator("input[name='cdBemPermIni-1-3']").fill(num_patrimonial)

    logger.info("Seção das etiquetas preenchidas.")