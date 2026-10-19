from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def preencher_dados_gerais(page: Page, caracteristica: str = "MARCA AUTOMATIZADA", tamanho: str = "100") -> None:
    logger.info("Preenchendo dados gerais.")

    ctx = escopo(page)

    ctx.locator("button[name='submitCancel']").click()
    aguardar_ajax_global(page)

    # Preenche o nome da característica
    logger.info("Preenchendo nome '{}'.", caracteristica)
    ctx.locator("input[name='nmCaracteristica']").click()
    ctx.locator("input[name='nmCaracteristica']").fill(caracteristica)

    # Preenche o tamanho
    logger.info("Preenchendo tamanho '{}'.", tamanho)
    ctx.locator("input[name='nrTamanho']").click()
    ctx.locator("input[name='nrTamanho']").fill(tamanho)

    # Deixar tabelado
    ctx.locator("input[name='inTabelado'][value='S']").click()

    ctx.locator("button[name='submitFinish']").click()

    esperar_sucesso_ou_erro(ctx)

    logger.info("Preenchimento de dados gerais finalizado.")
