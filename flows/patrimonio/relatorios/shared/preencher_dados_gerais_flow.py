from loguru import logger
from playwright.sync_api import Page, expect

from utils.competencia_financeira import obter_data_patrimonio
from utils.versao import escopo
from utils.waits import preencher_campo


def preencher_dados_gerais(page: Page, ug_data: dict[str, str]) -> None:
    logger.info("Iniciou o preenchimento dos dados gerais.")

    ctx = escopo(page)

    select_ug = ctx.locator("select[name='listaUg']")
    input_ug = ctx.locator("input[name='cdUg']")
    expect(select_ug.or_(input_ug).first).to_be_visible()

    if not select_ug.is_visible():
        preencher_campo(ctx, "input[name='cdUg']", ug_data["codigo"])

    ano_atual, mes_atual = obter_data_patrimonio(page, formato="YYYY/MM").split("/")

    ctx.type("input[name='anoMesInicial']", f"{ano_atual}01", delay=50)
    ctx.type("input[name='anoMesFinal']", f"{ano_atual}{mes_atual}", delay=50)

    logger.info("Finalizou o preenchimento dos dados gerais.")
