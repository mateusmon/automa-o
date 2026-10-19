from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import preencher_campo


def preencher_ug(page: Page, ug: dict[str, str]) -> None:
    """Preenche a UG, apenas se ainda não estiver com o valor esperado."""
    logger.info("Preenchendo UG {}.", ug["nome"])

    ctx = escopo(page)
    ug_locator = ctx.locator('input[name="ug"]')
    ug_locator.wait_for(state="visible")

    if ug["nome"] not in ug_locator.input_value():
        preencher_campo(ctx, 'input[name="ug"]', ug["codigo"])

    logger.info("UG preenchida {}.", ug["nome"])