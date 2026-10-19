from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def consultar_transferencia(page: Page, ug: dict[str, str], ul: dict[str, str]) -> None:

    logger.info("Iniciou consulta da transferência interna para a UG '{}'.", ug["sigla"])

    ctx = escopo(page)

    preencher_campo(ctx, "input[name='model-2']", ug["codigo"])
    preencher_campo(ctx, "input[name='model-7']", ul["sigla"])

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta da transferência interna para a UG '{}'.", ug["sigla"])
