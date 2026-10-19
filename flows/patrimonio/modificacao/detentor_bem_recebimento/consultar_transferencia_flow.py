from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def consultar_transferencia(page: Page, ug: dict[str, str]) -> None:
    logger.info("Iniciou consulta de transferência de detentor do bem pelo campo de UG: '{}'.", ug["codigo"])

    ctx = escopo(page)

    preencher_campo(ctx, "input[name='model-2']", ug["codigo"])

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de transferência de detentor do bem pelo campo de UG: '{}'.", ug["codigo"])
