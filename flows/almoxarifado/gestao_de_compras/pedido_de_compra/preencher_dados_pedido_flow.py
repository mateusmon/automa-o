from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def preencher_dados_pedido(page: Page, ua: dict[str, str]) -> None:
    logger.info("Iniciou preenchimento de dados do pedido de compra.")

    ctx = escopo(page)
    _preencher(ctx, page, ua)

    logger.info("Finalizou preenchimento de dados do pedido de compra.")


def _preencher(ctx, page: Page, ua: dict[str, str]) -> None:
    campo_ua = ctx.locator("input[name='cdUa']")

    campo_ua.wait_for(state="visible")

    logger.info("Preenchendo UA '{}'.", ua["sigla"])
    preencher_campo(ctx, "input[name='cdUa']", ua["sigla"])
    aguardar_ajax_global(page)

    logger.info("Preenchendo objeto do pedido de compra 'PEDIDO DE COMPRA DE MATERIAL DE CONSUMO'.")
    ctx.locator("textarea[name='objeto']").type("PEDIDO DE COMPRA DE MATERIAL DE CONSUMO", delay=50)
    logger.info("Preenchendo justificativa do pedido de compra 'REPOSIÇÃO DE ESTOQUE'.")
    ctx.locator("textarea[name='dsJustificativa']").type("REPOSIÇÃO DE ESTOQUE", delay=50)
