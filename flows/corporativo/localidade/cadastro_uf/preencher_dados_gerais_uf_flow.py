from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo


def preencher_dados_gerais_uf(page: Page, uf: dict) -> None:
    """
    Preenche a UF e confirma. Cenário A.
    Campos: Nome (`nmUf`), País (`pais`, lookup) e Sigla (`sgUf`); Código gerado.

    :param uf: dict do blueprint (nome, pais, sigla).
    """
    logger.info("Iniciou preenchimento de dados gerais de UF '{}'.", uf["nome"])

    ctx = escopo(page)

    aguardar_ajax_global(page)
    ctx.locator("input[name='nmUf']").wait_for(state="visible")
    logger.info("Preenchendo Nome de UF - Unidade da Federação: '{}'.", uf["nome"])
    ctx.locator("input[name='nmUf']").fill(uf["nome"])
    preencher_campo(ctx, "input[name='pais']", uf["pais"])
    logger.info("Preenchendo Sigla de UF - Unidade da Federação: '{}'.", uf["sigla"])
    ctx.locator("input[name='sgUf']").fill(uf["sigla"])

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou preenchimento de dados gerais de UF '{}'.", uf["nome"])
