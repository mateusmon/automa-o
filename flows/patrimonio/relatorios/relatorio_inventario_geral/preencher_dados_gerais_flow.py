from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_patrimonio
from utils.versao import escopo
from utils.waits import preencher_autocomplete_select


def preencher_dados_gerais(page: Page, ug_data: dict[str, str]) -> None:
    logger.info("Iniciou o preenchimento dos dados gerais.")

    ctx = escopo(page)

    campo_ug = ctx.locator("input[name='ug']")
    campo_ug.wait_for(state="visible")
    if not campo_ug.input_value().strip():
        preencher_autocomplete_select(ctx, "input[name='ug']", ug_data["codigo"])

    data_atual = obter_data_patrimonio(page, formato="DDMMYYYY")

    ctx.type("input[name='dtReferencia']", data_atual, delay=50)

    logger.info("Finalizou o preenchimento dos dados gerais.")
