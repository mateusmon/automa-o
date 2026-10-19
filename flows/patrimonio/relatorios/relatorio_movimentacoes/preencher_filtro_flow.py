from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_patrimonio
from utils.versao import escopo


def preencher_filtro(page: Page):
    logger.info("Preenchendo filtro.")

    ctx = escopo(page)

    data = obter_data_patrimonio(page, formato="DDMMYYYY")

    ctx.locator("input[name='dataIni']").click()
    ctx.locator("input[name='dataIni']").type(data, delay=50)
    ctx.locator("input[name='dataFim']").click()
    ctx.locator("input[name='dataFim']").type(data, delay=50)

    logger.info("Filtro preenchido.")
