from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo


def preencher_dados_gerais(page: Page, almoxarifado: dict, quantidade: str = "30") -> bool:
    logger.info("Iniciou preenchimento de dados gerais da política de compras de baixa frequência no almoxarifado '{}'.", almoxarifado["sigla"])

    ctx = escopo(page)

    logger.info("Preenchendo sigla do almoxarifado: '{}'.", almoxarifado["sigla"])
    preencher_campo(ctx, "input[name='cdAlmoxarifado']", almoxarifado["sigla"])
    aguardar_ajax_global(page)

    linha = ctx.locator("table.tabela tbody tr").first

    if linha.count() == 0:
        logger.info("Nenhum material de baixa frequência encontrado.")
        return False

    logger.info("Preenchendo quantidade de baixa frequência: '{}'.", quantidade)
    linha.locator("input[type='text']").dblclick()
    linha.locator("input[type='text']").fill(quantidade)
    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou preenchimento de dados gerais da política de compras de baixa frequência.")
    return True
