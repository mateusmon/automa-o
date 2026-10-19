from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def preencher_dados_gerais_pais(page: Page, pais: dict) -> None:
    """
    Preenche o País e confirma. Cenário A (só muda o escopo via `escopo(page)`).
    Campos: Nome (`nmPais`) e Sigla (`sgPais`); Código é gerado pelo sistema.

    :param pais: dict do blueprint (nome, sigla).
    """
    logger.info("Iniciou preenchimento de dados gerais de País '{}'.", pais["nome"])

    ctx = escopo(page)

    aguardar_ajax_global(page)
    ctx.locator("input[name='nmPais']").wait_for(state="visible")
    logger.info("Preenchendo Nome de País: '{}'.", pais["nome"])
    ctx.locator("input[name='nmPais']").fill(pais["nome"])
    logger.info("Preenchendo Sigla de País: '{}'.", pais["sigla"])
    ctx.locator("input[name='sgPais']").fill(pais["sigla"])

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou preenchimento de dados gerais de País '{}'.", pais["nome"])
