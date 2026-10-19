from typing import Literal

from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_patrimonio
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo, select_tipo


def preencher_detalhamento(
    page: Page, 
    fornecedor: dict[str, str], 
    tipo: Literal[
        "COMPRA EXTRA ORÇAMENTÁRIA",
        "IMPORTAÇÃO (ORÇ)",
        "DOAÇAO",
        "COMPRA",
        "COMODATO"
    ] = "COMPRA"
) -> bool:

    logger.info("Iniciou preenchimento de detalhamento para o tipo '{}'.", tipo)

    ctx = escopo(page)

    page.wait_for_load_state("domcontentloaded")
    aguardar_ajax_global(page)

    data_mes_aberto = obter_data_patrimonio(page, formato="DDMMYYYY")

    ha_opcao = select_tipo(ctx, "tipoBemFormaOperacao", tipo)

    if not ha_opcao:
        logger.warning("Este cliente não possui entrada do tipo {}", tipo)
        return False
    
    data_recebimento_input = ctx.locator('input[name="dtAquisicao"]')
    data_recebimento_input.clear()
    data_recebimento_input.press_sequentially(data_mes_aberto, delay=50)

    data_contabilizacao_input = ctx.locator('input[name="txDtContabil"]').or_(ctx.locator("input[name='dtContabil']"))

    aguardar_ajax_global(page)

    if data_contabilizacao_input.is_visible() and data_contabilizacao_input.is_enabled():
        data_contabilizacao_input.clear()
        data_contabilizacao_input.press_sequentially(data_mes_aberto, delay=50)
        ctx.get_by_text("Data de Contabilização:").click()
        aguardar_ajax_global(page)

        ctx.get_by_text("Data de Contabilização:").click()

    aguardar_ajax_global(page)
    
    preencher_campo(ctx, 'input[name="agente"]', fornecedor["nome"])

    logger.info("Finalizou preenchimento de detalhamento para o tipo '{}'.", tipo)
    return True
