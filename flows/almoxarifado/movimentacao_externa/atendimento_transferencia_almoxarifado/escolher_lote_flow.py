from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def escolher_lote(page: Page) -> None:
    logger.info("Iniciou escolha do primeiro lote disponível.")

    ctx = escopo(page)
    _escolher(ctx, page)

    logger.info("Finalizou escolha do primeiro lote disponível.")


def _escolher(ctx, page: Page) -> None:
    linha = ctx.locator("table tbody[name='MovimentosTitles'] tr").first
    coluna = linha.locator("td").count()

    ctx.locator(f"button[name='edit-qtPedidoPendente-1-1-{coluna}']").click()
    aguardar_ajax_global(page)

    linhas_ultima_tabela = ctx.locator(".tabela").last.locator("tbody tr")

    if linhas_ultima_tabela.count() == 0:
        logger.info("Nenhum lote disponível. Retornando sem selecionar.")
        ctx.locator("button[name='submitBack']").click()
        aguardar_ajax_global(page)
        return

    logger.info("Selecionando o primeiro lote disponível.")
    ctx.locator("input[name='qtAtendidoLote-1-6']").type("1", delay=50)

    page.wait_for_timeout(1_000)  # Espera para visualização

    ctx.locator("button[name='submitBack']").click()
    aguardar_ajax_global(page)