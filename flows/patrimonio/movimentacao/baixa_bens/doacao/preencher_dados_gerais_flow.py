from typing import Literal

from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_patrimonio
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo, select_tipo


def preencher_dados_gerais(
        page: Page,
        ug: dict[str, str],
        tipo_bem: Literal[
            "DE TERCEIROS ",
            "PRÓPRIO CONTABILIZADO",
            "PRÓPRIO CONTROLADO"
        ] = "PRÓPRIO CONTABILIZADO",
        tipo_baixa: Literal[
            "CADASTRAMENTO INDEVIDO",
            "EXTRAVIO OU SINISTRO",
            "DOAÇAO"
        ] = "DOAÇAO"
) -> None:
    
    logger.info("Iniciou preenchimento de dados gerais.")

    ctx = escopo(page)

    preencher_campo(ctx, "input[name='ug']", ug["codigo"])

    select_tipo(ctx, "tipoBem", tipo_bem)
    aguardar_ajax_global(page)

    data = obter_data_patrimonio(page, formato="DDMMYYYY")

    select_tipo(ctx, "situacaoBaixa", "AUTORIZADA")
    aguardar_ajax_global(page)

    if ctx.locator("input[name='dtContabil']").is_enabled():
        ctx.locator("input[name='dtContabil']").type(data, delay=50)

    select_tipo(ctx, "formaOperacao", tipo_baixa )
    aguardar_ajax_global(page)

    if ctx.locator("input[name='destino']").is_visible():
        preencher_campo(ctx, "input[name='destino']", "   ")

    logger.info("Finalizou preenchimento de dados gerais.")
