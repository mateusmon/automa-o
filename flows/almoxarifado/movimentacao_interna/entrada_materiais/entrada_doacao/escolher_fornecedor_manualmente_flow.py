from loguru import logger
from playwright.sync_api import Page, expect

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def escolher_fornecedor_manualmente(page: Page) -> None:
    logger.info("Iniciou escolha de fornecedor.")

    ctx = escopo(page)
    _escolher(ctx, page)

    logger.info("Finalizou escolha de fornecedor.")


def _escolher(ctx, page: Page) -> None:
    ctx.locator('button[name="lookup-agenteEntrada"]').click()
    aguardar_ajax_global(page)

    ctx.get_by_title("Consultar novo registro").click()
    aguardar_ajax_global(page)

    primeira_linha = ctx.locator('tr[name="searchResultData"][model="model-0"]')
    segunda_linha = ctx.locator('tr[name="searchResultData"][model="model-1"]')
    celula = primeira_linha.locator('td[name="cell-1-2"]')

    if celula.inner_text() == "":
        botao_anexar = segunda_linha.locator('button[name="submitUse"]')
    else:
        botao_anexar = primeira_linha.locator('button[name="submitUse"]')

    if botao_anexar.is_visible():
        logger.info("Anexando primeiro fornecedor encontrado na tabela.")
        botao_anexar.click()

    aguardar_ajax_global(page)
