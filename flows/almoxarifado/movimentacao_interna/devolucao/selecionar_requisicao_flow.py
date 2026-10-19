from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def selecionar_requisicao_devolucao(page: Page, almoxarifado: dict[str, str]) -> bool:
    logger.info("Iniciou seleção de requisição para devolução no almoxarifado '{}'.", almoxarifado["nome"])

    ctx = escopo(page)

    ctx.locator("button[name='lookup-nrDocumento-1-3']").click()
    aguardar_ajax_global(page)

    logger.info("Preenchendo sigla do almoxarifado: '{}'.", almoxarifado["sigla"])
    preencher_campo(ctx, ctx.locator("input[name='model-2']"), almoxarifado["sigla"])

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    linhas = ctx.locator("table[name='paginationTable'] tbody tr")

    if linhas.count() == 0:
        logger.info("Não há requisições finalizadas para devolver no almoxarifado '{}'.", almoxarifado["sigla"])
        return False

    logger.info("Selecionando a primeira requisição para devolução.")
    linhas.first.locator("button[name='submitUse']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou seleção de requisição para devolução no almoxarifado '{}'.", almoxarifado["sigla"])
    return True
