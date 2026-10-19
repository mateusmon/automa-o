from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def preencher_dados_gerais(page: Page, almoxarifado_data: dict) -> None:
    logger.info("Preenchendo dados gerais do nível de estoque do almoxarifado '{}'.", almoxarifado_data["sigla"])

    ctx = escopo(page)

    logger.info("Preenchendo sigla do almoxarifado '{}'.", almoxarifado_data["sigla"])
    preencher_campo(ctx, "input[name='cdAlmoxarifado']", almoxarifado_data["sigla"])
    radio = ctx.locator("input[name='nivelEstoque'][value='4']")
    radio.check()

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)
    
    logger.info("Preenchimento de dados gerais do nível de estoque do almoxarifado '{}' finalizado.", almoxarifado_data["sigla"])
