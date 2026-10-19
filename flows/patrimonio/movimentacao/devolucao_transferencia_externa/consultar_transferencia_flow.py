from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo, selecionar_resultado


def consultar_transferencia(page: Page, ug: dict[str, str], ul: dict[str, str]) -> None:

    logger.info("Iniciou consulta da transferência externa na UG '{}'.", ug["nome"])

    ctx = escopo(page)

    preencher_campo(ctx, "input[name='model-2']", ug["codigo"])
    aguardar_ajax_global(page)

    titulo = ctx.get_by_text("U.G. - Resultado da Consulta").is_visible()

    if titulo:
        selecionar_resultado(ctx, "table[name='paginationTable'] tbody tr", 3, ug["codigo"])

    preencher_campo(ctx, "input[name='model-5']", ul["sigla"])
    aguardar_ajax_global(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta da transferência externa na UG '{}'.", ug["nome"])