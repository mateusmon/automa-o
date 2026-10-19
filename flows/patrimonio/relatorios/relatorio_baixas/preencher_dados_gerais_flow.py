from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_patrimonio
from utils.versao import escopo
from utils.waits import preencher_campo


def preencher_dados_gerais(page: Page, ug: dict[str, str]):
    logger.info("Preenchendo dados gerais.")

    ctx = escopo(page)

    data = obter_data_patrimonio(page, formato="YYYYMM")

    select_ug = ctx.locator("select[name='listaUg']")
    campo_ug = ctx.locator("input[name='cdUg']")
    select_ug.or_(campo_ug).first.wait_for(state="visible")

    if not select_ug.is_visible():
        preencher_campo(ctx, campo_ug, ug["codigo"])

    ctx.locator("input[name='anoMesInicial']").click()
    ctx.locator("input[name='anoMesInicial']").type(data, delay=50)
    ctx.locator("input[name='anoMesFinal']").click()
    ctx.locator("input[name='anoMesFinal']").type(data, delay=50)

    logger.info("Dados gerais preenchido.")
