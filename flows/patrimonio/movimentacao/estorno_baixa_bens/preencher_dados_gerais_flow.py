from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_patrimonio
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def preencher_dados_gerais(page: Page, justificativa: str = "Uma boa justificativa.") -> None:
    logger.info("Preenchendo dados gerais. Justificativa: '{}'.", justificativa)

    ctx = escopo(page)

    data = obter_data_patrimonio(page, formato="DDMMYYYY")
    logger.info("Data de estorno obtida: '{}'.", data)
    ctx.locator("textarea[name='txJustBaixaEstorno']").fill(justificativa)
    ctx.locator("input[name='dtEstorno-1-5']").type(data, delay=50)

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Dados gerais preenchidos. Justificativa: '{}'.", justificativa)
