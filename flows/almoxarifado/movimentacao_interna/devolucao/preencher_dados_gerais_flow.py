from loguru import logger
from playwright.sync_api import Page, expect

from utils.competencia_financeira import obter_data_almoxarifado
from utils.versao import escopo
from utils.waits import preencher_campo


def preencher_dados_gerais(page: Page, almoxarifado: dict[str, str], ur: dict[str, str]) -> None:
    logger.info("Iniciou preenchimento de dados gerais da devolução no almoxarifado '{}'.", almoxarifado["nome"])

    ctx = escopo(page)

    logger.info("Preenchendo sigla do almoxarifado: '{}'.", almoxarifado["sigla"])
    preencher_campo(ctx, "input[name='almoxarifado']", almoxarifado["sigla"])
    expect(ctx.locator('input[name="ug"]')).not_to_have_value("")

    data_hoje = obter_data_almoxarifado(page, "DDMMYYYY")
    campo_data = ctx.locator('input[name="dtRecebimento"]')
    if campo_data.is_enabled():
        logger.info("Preenchendo data de recebimento: '{}'.", data_hoje)
        campo_data.clear()
        campo_data.type(data_hoje, delay=50)

    logger.info("Preenchendo UR: '{}'.", ur["nome"])
    preencher_campo(ctx, "input[name='agenteEntrada']", ur["nome"])

    logger.info("Finalizou preenchimento de dados gerais da devolução no almoxarifado '{}'.", almoxarifado["nome"])
