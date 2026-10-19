from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.competencia_financeira import obter_data_patrimonio
from utils.waits import clicar_com_ajax, select_tipo


def preencher_observacoes(page: Page) -> None:
    logger.info("Iniciou o preenchimento de observações.")

    ctx = escopo(page)

    data = obter_data_patrimonio(page, formato="DDMMYYYY")

    logger.info("Navegando para aba 'Observações'.")
    clicar_com_ajax(ctx, "button[name='submitTabObservacoes']")

    clicar_com_ajax(ctx, "button[name='submitAddLine1']")

    logger.info("Preenchendo data de observação: '{}'.", data)
    campo_data = ctx.locator("input[name='dtObs']")
    campo_data.clear()
    campo_data.type(data, delay=50)

    logger.info("Selecionando Finalidade: 'OBSERVAÇÃO'.")
    select_tipo(ctx, "tipoObs", "OBSERVAÇÃO")

    logger.info("Preenchendo campo Observações: 'OBSERVAÇÃO DE TESTE AUTOMATIZADO.'.")
    ctx.locator("textarea[name='dsObs']").fill("OBSERVAÇÃO DE TESTE AUTOMATIZADO.")

    clicar_com_ajax(ctx, "button[name='submitBack']")

    logger.info("Finalizou o preenchimento de observações.")