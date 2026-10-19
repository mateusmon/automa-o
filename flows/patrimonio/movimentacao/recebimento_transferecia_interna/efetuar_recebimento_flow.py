from loguru import logger
from playwright.sync_api import Page, expect

from utils.competencia_financeira import obter_data_patrimonio
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def efetuar_recebimento(page: Page) -> None:
    logger.info("Iniciou confirmação de recebimento de transferência interna.")

    ctx = escopo(page)

    data = obter_data_patrimonio(page, formato="DD/MM/YYYY")

    campo_data_operacao = ctx.locator("input[name='dtOperacao']")
    campo_data_operacao.clear()
    campo_data_operacao.fill(data)
    ctx.click("button[name='submitFinish']")
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou confirmação de recebimento de transferência interna.")
