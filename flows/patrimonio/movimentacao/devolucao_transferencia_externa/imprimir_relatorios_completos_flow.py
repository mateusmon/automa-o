from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import clicar_com_ajax, select_tipo
from flows.shared.imprimir_relatorio_flow import imprimir_relatorio


def imprimir_relatorios_completos(page: Page) -> None:
    logger.info("Iniciou a impressão dos relatórios completos.")

    ctx = escopo(page)

    clicar_com_ajax(ctx, ctx.locator("input[name='submitMarkAll1']"))

    logger.info("Selecionando Tipo de Relatório: 'HTML'.")
    select_tipo(ctx, "formatosPossiveisSaida-1-4", "HTML")

    logger.info("Selecionando Tipo de Relatório: 'PDF'.")
    select_tipo(ctx, "formatosPossiveisSaida-1-4", "PDF")

    clicar_com_ajax(ctx, "button[name='submitPrint']")
    imprimir_relatorio(page, ja_solicitado=True)

    logger.info("Finalizou a impressão dos relatórios completos.")