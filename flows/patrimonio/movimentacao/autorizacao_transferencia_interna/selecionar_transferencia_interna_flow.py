from loguru import logger
from playwright.sync_api import Page

from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo

def selecionar_transferencia_interna(page: Page, ug: dict[str, str], ul: dict[str, str]) -> bool:
    logger.info("Selecionando Transferência Interna para a UL '{}'.", ul["unidade_administrativa"])

    ctx = escopo(page)

    preencher_campo(ctx, "input[name='model-2']", ug["codigo"])
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    ha_transferencia = selecionar_movimentacao(page, ul["unidade_administrativa"])

    if not ha_transferencia:
        logger.info("Não há nenhuma transferência interna para a UL '{}'.", ul["unidade_administrativa"])
        return ha_transferencia

    logger.info("Transferência Interna selecionada para a UL '{}'.", ul["unidade_administrativa"])

    return ha_transferencia