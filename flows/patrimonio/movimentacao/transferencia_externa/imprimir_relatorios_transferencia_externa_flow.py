from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, clicar_com_ajax, select_tipo
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio


def imprimir_relatorios_transferencia_externa(page: Page) -> None:
    logger.info("Iniciou a impressão de relatórios da Transferência Externa .")

    ctx = escopo(page)

    clicar_com_ajax(ctx, ctx.locator("input[name='submitMarkAll1']"))
    aguardar_ajax_global(page)

    logger.info("Selecionando formato de saída 'HTML'.")
    select_tipo(ctx, "formatosPossiveisSaida-1-4", "HTML")

    logger.info("Selecionando formato de saída 'PDF'.")
    select_tipo(ctx, "formatosPossiveisSaida-1-4", "PDF")

    clicar_com_ajax(ctx, ctx.locator("button[name='submitPrint']"))
    imprimir_relatorio(page, ja_solicitado=True)

    logger.info("Finalizou a impressão de relatórios da Transferência Externa.")