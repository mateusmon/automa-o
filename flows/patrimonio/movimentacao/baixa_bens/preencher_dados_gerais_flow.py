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
            "INDEVIDO",
            "EXTRAVIO",
            "DOAÇAO"
        ] = "DOAÇAO"
) -> None:
    
    logger.info("Iniciou preenchimento de dados gerais para a unidade gestora '{}'.", ug["nome"])

    ctx = escopo(page)

    data = obter_data_patrimonio(page, formato="DD/MM/YYYY")

    preencher_campo(ctx, "input[name='ug']", ug["codigo"])

    select_tipo(ctx, "tipoBem", tipo_bem)
    aguardar_ajax_global(page)

    select_tipo(ctx, "formaOperacao", tipo_baixa )
    aguardar_ajax_global(page)

    campo_destino = ctx.locator("input[name='destino']")
    if campo_destino.is_visible() and campo_destino.is_enabled():
        preencher_campo(ctx, "input[name='destino']", "   ")

    campo_data = ctx.locator("input[name='dtContabil']")
    if campo_data.is_visible() and campo_data.is_enabled():
        ctx.locator("input[name='dtContabil']").fill(data)

    logger.info("Finalizou preenchimento de dados gerais para a unidade gestora '{}', tipo de bem '{}', tipo de baixa '{}', data '{}'.", ug["nome"], tipo_bem, tipo_baixa, data)
