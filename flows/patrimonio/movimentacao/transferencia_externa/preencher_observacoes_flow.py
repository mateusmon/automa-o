from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_patrimonio
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, clicar_com_ajax, select_tipo


def preencher_observacoes(page: Page) -> None:
    logger.info("Iniciou o preenchimento da aba 'Observações'.")

    ctx = escopo(page)

    clicar_com_ajax(ctx, ctx.locator("button[name='submitTabObservacoes']"))
    clicar_com_ajax(ctx, ctx.locator("button[name='submitAddLine1']"))

    data_hoje = obter_data_patrimonio(page, formato="DDMMYYYY")

    logger.info("Preenchendo data de observação: '{}'.", data_hoje)
    data_input = ctx.locator('input[name="dtObs"]')
    data_input.clear()
    data_input.type(data_hoje, delay=50)

    if select_tipo(ctx, "tipoObs", "AVISO"):
        logger.info("Selecionando finalidade da observação 'AVISO'.")
    else:
        logger.warning("Mantendo finalidade de observação 'OBSERVAÇÃO'.")

    aguardar_ajax_global(page)

    logger.info("Preenchendo observação: 'OBSERVAÇÃO DE TRANSFERÊNCIA EXTERNA AUTOMATIZADA'.")
    ctx.locator('textarea[name="dsObs"]').fill("OBSERVAÇÃO DE TRANSFERÊNCIA EXTERNA AUTOMATIZADA")
    clicar_com_ajax(ctx, ctx.locator("button[name='submitBack']"))
    
    logger.info("Finalizou o preenchimento da aba 'Observações'.")