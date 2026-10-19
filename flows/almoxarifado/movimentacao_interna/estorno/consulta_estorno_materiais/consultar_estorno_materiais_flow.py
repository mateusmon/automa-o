from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def consultar_estorno_materiais(page: Page, funcionario: dict[str, str]) -> None:
    logger.info(
        "Iniciou consulta de estorno de materiais para funcionário: {nome}",
        nome=funcionario["nome"],
    )

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Preenchendo nome do funcionário: '{}'.", funcionario["nome"])
    preencher_campo(ctx, ctx.locator("input[name='model-4']"), funcionario["nome"])
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info(
        "Finalizou consulta de estorno de materiais para funcionário: {nome}.",
        nome=funcionario["nome"],
    )
