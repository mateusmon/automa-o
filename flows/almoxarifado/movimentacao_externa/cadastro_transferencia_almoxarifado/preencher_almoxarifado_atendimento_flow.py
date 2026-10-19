from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_almoxarifado
from utils.versao import escopo
from utils.waits import preencher_campo


def preencher_almoxarifado_atendimento(page: Page, almoxarifado: dict) -> None:
    logger.info(
        "Iniciou preenchimento de almoxarifado de atendimento '{}'.",
        almoxarifado["nome"],
    )

    ctx = escopo(page)
    if ctx.locator("input[name='dtRequisicao']").is_enabled():
        data_almox = obter_data_almoxarifado(page, "DDMMYYYY")
        ctx.locator("input[name='dtRequisicao']").clear()
        ctx.locator("input[name='dtRequisicao']").press_sequentially(
            data_almox, delay=50
        )

    logger.info(
        "Preenchendo sigla do almoxarifado de atendimento: '{}'.", almoxarifado["sigla"]
    )
    preencher_campo(ctx, "input[name='almoxarifado']", almoxarifado["sigla"])

    logger.info(
        "Finalizou preenchimento de almoxarifado de atendimento '{}'.",
        almoxarifado["nome"],
    )
