
from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_patrimonio
from utils.versao import escopo
from utils.waits import select_tipo


def preencher_demais_dados(page: Page) -> None:
    logger.info("Iniciou o preenchimento dos demais dados.")

    ctx = escopo(page)

    data_hoje = obter_data_patrimonio(page, "DDMMYYYY")

    ctx.locator("button[name='submitFinish']").wait_for(state="visible")

    ctx.locator("input[name='dtAtendimento']").type(data_hoje, delay=50)
    logger.info("Preencheu a data de atendimento com '{}'.", data_hoje)
    ctx.locator("input[name='qtAtendida-1-4']").fill("1")

    select_tipo(ctx, "cdTpAtendimentoReq-1-5", "NORMAL")
    
    logger.info("Finalizou o preenchimento dos demais dados.")
