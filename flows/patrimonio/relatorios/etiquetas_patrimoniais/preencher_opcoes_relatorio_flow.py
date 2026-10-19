from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, select_tipo


def preencher_opcoes_relatorio(page: Page):
    logger.info("Preenchendo opções de Relatório.")

    ctx = escopo(page)

    # Selecionar Fabricante
    if ctx.locator("select[name='idFabricanteEtiqueta'] option").count() > 0:
        select_tipo(ctx, "idFabricanteEtiqueta", "INFORMS")
        aguardar_ajax_global(page)

    # Selecionar Tipo de Folha
    if ctx.locator("select[name='tipoFolhaEtiqueta'] option").count() > 0:
        select_tipo(ctx, "idTpFolhaEtiqueta", "A4")
        aguardar_ajax_global(page)



    logger.info("Opções de Relatório preenchidos.")