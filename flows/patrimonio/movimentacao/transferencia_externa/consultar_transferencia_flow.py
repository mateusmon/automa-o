from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_transferencia(page: Page, ug: dict[str, str]) -> None:

    logger.info("Iniciou consulta de transferência externa com UG: '{}'.", ug["codigo"])

    ctx = escopo(page)

    ctx.get_by_role("button", name="Consulta", exact=True).click()
    aguardar_ajax_global(page)

    ctx.locator("input[name='model-2']").type(ug["codigo"], delay=50)
    ctx.locator("button[name='lookup-model-2']").click()
    aguardar_ajax_global(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de transferência externa com UG: '{}'.", ug["codigo"])
