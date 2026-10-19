from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_almoxarifado
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo


def preencher_dados(
    page: Page, almoxarifado: dict, material: dict, quantidade: str = "1"
) -> None:
    logger.info(
        "Iniciou preenchimento de dados da transferência entre endereços no almoxarifado '{}'.",
        almoxarifado["nome"],
    )

    ctx = escopo(page)

    logger.info("Preenchendo sigla do almoxarifado: '{}'.", almoxarifado["sigla"])
    preencher_campo(ctx, "input[name='almoxarifado']", almoxarifado["sigla"])
    logger.info("Preenchendo nome do material: '{}'.", material["nome"])
    preencher_campo(ctx, "input[name='cdBemServico']", material["nome"])

    logger.info("Preenchendo quantidade de transferência: '{}'.", quantidade)
    fild_qtd = ctx.locator("input[name='qtTransf']")
    fild_qtd.dblclick()
    fild_qtd.fill(quantidade)

    if ctx.locator("input[name='qtLote-1-5']").is_visible():
        logger.info("Preenchendo quantidade de lote: '{}'.", quantidade)
        ctx.locator("input[name='qtLote-1-5']").fill(quantidade)

    if ctx.locator("input[name='dtContabil']").is_enabled():
        logger.info("Preenchendo Data Contábil")
        ctx.locator("input[name='dtContabil']").clear()
        ctx.locator("input[name='dtContabil']").press_sequentially(
            obter_data_almoxarifado(page, "DDMMYYYY"), delay=5
        )

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info(
        "Finalizou preenchimento de dados da transferência entre endereços no almoxarifado '{}'.",
        almoxarifado["nome"],
    )
