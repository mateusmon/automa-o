from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_patrimonio
from utils.versao import escopo
from utils.waits import preencher_campo


def preencher_dados_gerais(page: Page, ug_data: dict[str, str], ul_data: dict[str, str]) -> None:
    logger.info("Iniciou o preenchimento dos dados gerais. UG: '{}', UL: '{}'.", ug_data["codigo"], ul_data["sigla"])

    ctx = escopo(page)

    preencher_campo(ctx, "input[name='cdUg']", ug_data["codigo"])
    preencher_campo(ctx, "input[name='cdUl']", ul_data["sigla"])

    data = obter_data_patrimonio(page, formato="DDMMYYYY")
    ctx.locator("input[name='dtRequisicao']").clear()
    ctx.locator("input[name='dtRequisicao']").press_sequentially(data, delay=50)
    
    logger.info("Finalizou o preenchimento dos dados gerais. UG: '{}', UL: '{}'.", ug_data["codigo"], ul_data["sigla"])
