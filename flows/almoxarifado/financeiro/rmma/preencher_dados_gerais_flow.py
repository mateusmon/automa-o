from datetime import datetime

from dateutil.relativedelta import relativedelta
from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_almoxarifado
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def preencher_dados_gerais(page: Page, ug_data: dict, almoxarifado_data: dict) -> None:
    logger.info("Iniciou preenchimento de dados gerais para emissão de RMMA.")

    ctx = escopo(page)

    logger.info("Preenchendo código da UG '{}'.", ug_data["codigo"])
    preencher_campo(ctx, "input[name='model-0']", ug_data["codigo"])
    aguardar_ajax_global(page)
    if ctx.locator("input[name='model-1']").is_visible():
        logger.info("Preenchendo sigla do almoxarifado '{}'.", almoxarifado_data["sigla"])
        preencher_campo(ctx, "input[name='model-1']", almoxarifado_data["sigla"])

    competencia = obter_data_almoxarifado(page, formato="YYYYMM")
    dt_comp = datetime.strptime(competencia, "%Y%m")
    mes_anterior = (dt_comp - relativedelta(months=1)).strftime("%Y%m")

    logger.info("Preenchendo data com mês anterior '{}'.", mes_anterior)
    campo_data = ctx.locator("input[name='model-2-from']").or_(ctx.locator("input[name='model-1-from']"))
    campo_data.clear()
    campo_data.type(mes_anterior, delay=50)
    ctx.locator("input[name='model-2-to']").or_(ctx.locator("input[name='model-1-to']")).click()

    ctx.get_by_title("Consultar novo registro").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou preenchimento de dados gerais para emissão de RMMA.")
