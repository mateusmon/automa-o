from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def preencher_dados_gerais_unidade_medida(page: Page, unidade_medida: dict) -> None:
    """
    Preenche a Unidade de Medida e confirma. Cenário A (só muda o escopo via
    `escopo(page)`). Campos: Descrição (`dsUm`) e Sigla (`sgUm`, chave única);
    o Código é gerado pelo sistema.

    :param unidade_medida: dict do blueprint (descricao, sigla).
    """
    logger.info("Iniciou preenchimento de dados gerais de Unidade de Medida.")

    ctx = escopo(page)

    aguardar_ajax_global(page)
    ctx.locator("input[name='sgUm']").wait_for(state="visible")

    ctx.locator("input[name='dsUm']").fill(unidade_medida["descricao"])
    ctx.locator("input[name='sgUm']").fill(unidade_medida["sigla"])

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou preenchimento de dados gerais de Unidade de Medida.")
