from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_autocomplete, esperar_sucesso_ou_erro


def preencher_dados_gerais(page: Page, nome: str = "OBSERVAÇÃO AUTOMAÇÃO") -> None:

    logger.info("Preenchendo dados gerais.")

    ctx = escopo(page)

    logger.info("Preenchendo nome '{}'", nome)
    ctx.locator("input[name='nmTipoParecer']").click()
    ctx.locator("input[name='nmTipoParecer']").fill(nome)
    ctx.locator("button[name='submitAddLine1']").click()
    aguardar_ajax_global(page)
    preencher_autocomplete(ctx, "input[name='nmContexto-1-2']", "   ")
    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Preenchimento de dados gerais finalizado.")
