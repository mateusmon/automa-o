from datetime import datetime, timedelta

from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_almoxarifado
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def alterar_devolucao_materiais(page: Page) -> bool:
    logger.info("Iniciou alteração de devolução de materiais.")

    ctx = escopo(page)
    data_hoje = obter_data_almoxarifado(page, "DD/MM/YYYY")
    data_anterior = (datetime.strptime(data_hoje, "%d/%m/%Y") - timedelta(days=1)).strftime("%d/%m/%Y")

    campo_data = ctx.locator("input[name='dtRecebimento']")
    data_atual = campo_data.input_value()

    if campo_data.is_disabled():
        logger.warning("Campo de data de recebimento desabilitado. Não é possível fazer alteração.")
        return False

    if data_atual == data_hoje:
        nova_data = data_anterior
    else:
        nova_data = data_hoje

    logger.info("Alterando data de recebimento: '{}' -> '{}'.", data_atual, nova_data)
    campo_data.dblclick()
    campo_data.fill(nova_data)

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)

    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou alteração de devolução de materiais.")
    return True
