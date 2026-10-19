from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo, select_tipo


def preencher_dados(page: Page, material: dict[str, str]) -> None:
    logger.info("Iniciou preenchimento de dados para o material '{}'.", material["nome"])

    ctx = escopo(page)

    # Preenche Material
    logger.info("Preenchendo nome do material: '{}'.", material["nome"])
    preencher_campo(ctx, "input[name='cdBemServico-1-2']", material["nome"])

    # Seleciona Fabricante
    logger.info("Selecionando fabricante.")
    select_fabricante = ctx.locator("select[name='idFabricanteEtiqueta']")

    if select_fabricante.locator("option").count() > 1:
        logger.info("Selecionando etiqueta do fabricante: 'INFORMS'.")
        select_tipo(ctx, "idFabricanteEtiqueta", "INFORMS")
        aguardar_ajax_global(page)

    # Seleciona Tipo de folha
    select_folha = ctx.locator("select[name='idTpFolhaEtiqueta']")

    if select_folha.locator("option").count() > 1:
        logger.info("Selecionando tipo de folha: 'A4'.")
        select_tipo(ctx, "idTpFolhaEtiqueta", "A4")
        aguardar_ajax_global(page)

    logger.info("Finalizou preenchimento de dados para o material '{}'.", material["nome"])
