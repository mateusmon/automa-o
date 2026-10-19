from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, clicar_com_ajax


def escolher_lote(page: Page) -> None:
    logger.info("Iniciou escolha do primeiro lote disponível.")

    ctx = escopo(page)

    botao_locator = ctx.locator(".atendReqItem tbody tr").first.locator("button[name^='edit-qtPedidoPendente']")
    clicar_com_ajax(ctx, botao_locator)
    aguardar_ajax_global(page)

    if ctx.locator(".tabela").last.locator("tbody tr").count() == 0:
        logger.info("Nenhum lote disponível para escolher.")
        clicar_com_ajax(ctx, "button[name='submitBack']")
        aguardar_ajax_global(page)
        return

    logger.info("Escolhendo primeiro lote disponível.")
    ctx.locator("input[name='qtAtendidoLote-1-6']").fill("1")
    page.wait_for_timeout(1_000)
    clicar_com_ajax(ctx, "button[name='submitBack']")

    logger.info("Finalizou escolha do primeiro lote disponível.")
