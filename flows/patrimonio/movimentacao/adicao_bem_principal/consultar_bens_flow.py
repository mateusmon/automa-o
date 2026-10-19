from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def consultar_bens(page: Page, ul: dict[str, str], bem: dict[str, str]) -> None:
    logger.info("Iniciou consulta de bens {}.", bem["nome"])

    ctx = escopo(page)

    ctx.locator("button[name='lookup-cdBemPermPrincipal']").click()
    aguardar_ajax_global(page)

    preencher_campo(ctx, "input[name='model-7']", ul["sigla"])
    aguardar_ajax_global(page)

    preencher_campo(ctx, "input[name='model-15']", bem["nome"])
    aguardar_ajax_global(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    if ctx.locator("button[name='submitBack']").is_visible():
        ctx.locator("button[name='submitBack']").click()
        aguardar_ajax_global(page)

    logger.info("Finalizou consulta de bens {}.", bem["nome"])
