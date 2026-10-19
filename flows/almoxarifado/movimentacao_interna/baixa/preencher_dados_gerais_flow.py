from loguru import logger
from playwright.sync_api import Page, expect

from utils.competencia_financeira import obter_data_almoxarifado
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo, select_tipo


def preencher_dados_gerais(page: Page, almoxarifado: dict, modalidade: str | None, destino: dict | None = None, situacao: str | None = None) -> None:
    logger.info("Iniciou preenchimento de dados gerais da baixa no almoxarifado '{}'.", almoxarifado["nome"])

    ctx = escopo(page)

    logger.info("Preenchendo sigla do almoxarifado: '{}'.", almoxarifado["sigla"])
    preencher_campo(ctx, "input[name='almoxarifado']", almoxarifado["sigla"])
    expect(ctx.locator('input[name="ug"]')).not_to_have_value("")

    if modalidade:
        logger.info("Preenchendo modalidade da baixa: '{}'.", modalidade)
        select_tipo(ctx, "tipoMovimento", modalidade)
        aguardar_ajax_global(page)

    if destino:
        campo_destino = ctx.locator("input[name='orgaoExterno']")
        if campo_destino.is_visible() and campo_destino.is_enabled():
            logger.info("Preenchendo destino da baixa: '{}'.", destino.get("sigla", destino.get("nome", "")))
            preencher_campo(ctx, "input[name='orgaoExterno']", destino.get("sigla", destino.get("nome", "")))
            aguardar_ajax_global(page)

    if situacao:
        campo_situacao = ctx.locator("select[name='tipoSituacaoBaixa']")
        if campo_situacao.is_visible():
            logger.info("Selecionando tipo de situação da baixa: '{}'.", situacao)
            select_tipo(ctx, "tipoSituacaoBaixa", situacao)
            aguardar_ajax_global(page)

    logger.info("Preenchendo data da baixa com a data do almoxarifado '{}'.", almoxarifado["nome"])
    data_hoje = obter_data_almoxarifado(page, "DDMMYYYY")
    campo_data = ctx.locator('input[name="dtBaixa"]')
    campo_data.clear()
    campo_data.type(data_hoje, delay=50)

    logger.info("Finalizou preenchimento de dados gerais da baixa no almoxarifado '{}'.", almoxarifado["nome"])
