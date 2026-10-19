from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_patrimonio
from utils.versao import escopo
from utils.waits import preencher_campo


def preencher_dados_gerais(page: Page, ug_data: dict[str, str]) -> None:
    logger.info("Iniciou o preenchimento dos dados gerais.")

    ctx = escopo(page)

    select_ug = ctx.locator("select[name='listaUg']")
    campo = ctx.locator("input[name='cdUg']").or_(ctx.locator("input[name='ug']"))
    select_ug.or_(campo).first.wait_for(state="visible")

    if not select_ug.is_visible():
        campo = campo.first
        preencher_campo(ctx, campo, ug_data["codigo"])

    ano_atual, mes_atual = obter_data_patrimonio(page, formato="YYYY/MM").split("/")

    ctx.type("input[name='anoMesIni']", f"{ano_atual}01", delay=50)
    ctx.type("input[name='anoMesFim']", f"{ano_atual}{mes_atual}", delay=50)

    logger.info("Finalizou o preenchimento dos dados gerais.")
