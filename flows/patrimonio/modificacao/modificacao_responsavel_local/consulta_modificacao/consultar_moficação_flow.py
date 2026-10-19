from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def consultar_modificacao(page: Page, ug: dict[str, str], ua: dict[str, str]) -> None:
    logger.info("Iniciou consulta de modificação de responsável local {}.", ua["sigla"])

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    preencher_campo(ctx, "input[name='model-1']", ug["codigo"])
    preencher_campo(ctx, "input[name='model-3']", ua["sigla"])

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de modificação de responsável local {}.", ua["sigla"])
