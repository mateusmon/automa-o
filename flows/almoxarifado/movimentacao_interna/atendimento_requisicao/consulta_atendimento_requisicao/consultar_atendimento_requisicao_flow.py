from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def consultar_atendimento_requisicao(
    page: Page,
    almoxarifado: dict[str, str],
    ur: dict[str, str],
) -> None:
    logger.info("Iniciou consulta de atendimento de requisição no almoxarifado '{}'.", almoxarifado["nome"])

    ctx = escopo(page)
    _consultar(ctx, page, almoxarifado, ur)

    logger.info("Finalizou consulta de atendimento de requisição no almoxarifado '{}'.", almoxarifado["nome"])


def _consultar(ctx, page: Page, almoxarifado: dict, ur: dict) -> None:
    ctx.locator("button[name='submitSearch']").click()

    logger.info("Preenchendo sigla do almoxarifado: '{}'.", almoxarifado["sigla"])
    preencher_campo(ctx, ctx.locator("input[name='model-2']"), almoxarifado["sigla"])
    logger.info("Preenchendo nome da UR: '{}'.", ur["nome"])
    preencher_campo(ctx, ctx.locator("input[name='model-6']"), ur["nome"])
    logger.info("Preenchendo status do atendimento: 'ATENDIDA'.")
    linha_situacao = ctx.locator("tr").filter(has=ctx.locator("td", has_text="Situação:"))
    preencher_campo(ctx, linha_situacao.locator("input[type='text']"), "ATENDIDA")

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)
