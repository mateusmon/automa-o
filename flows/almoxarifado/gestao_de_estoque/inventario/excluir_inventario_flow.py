from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo


def excluir_inventario(page: Page, almoxarifado: dict) -> None:
    logger.info("Iniciou exclusão de inventário no almoxarifado '{}'.", almoxarifado["sigla"])

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Preenchendo sigla do almoxarifado '{}'.", almoxarifado["sigla"])
    preencher_campo(ctx, "input[name='model-1']", almoxarifado["sigla"])

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    linha = ctx.locator("table[name='paginationTable'] tbody tr").filter(
        has=ctx.locator("td").nth(1).filter(has_text=almoxarifado["nome"])
    ).first

    if linha.count() == 0:
        logger.info("Nenhum inventário encontrado para o almoxarifado '{}'.", almoxarifado["nome"])
        return

    linha.locator("button[name='submitUse']").click()
    aguardar_ajax_global(page)

    page.once("dialog", lambda dialog: dialog.accept())
    ctx.locator("button[name='submitDelete']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou exclusão de inventário no almoxarifado '{}'.", almoxarifado["sigla"])
