from datetime import datetime

from dateutil.relativedelta import relativedelta
from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_almoxarifado
from utils.versao import escopo
from utils.waits import preencher_campo


def preencher_dados_gerais(
    page: Page, ug: dict[str, str], almoxarifado: dict[str, str]
):
    logger.info(
        "Iniciou preenchimento de dados gerais no almoxarifado '{}'.",
        almoxarifado["nome"],
    )

    ctx = escopo(page)
    data_fim = obter_data_almoxarifado(page, formato="DDMMYYYY")

    dt_fim_obj = datetime.strptime(data_fim, "%d%m%Y")
    data_inicio = (dt_fim_obj - relativedelta(months=6)).strftime("%d%m%Y")

    # Preenche Período
    logger.info(
        "Preenchendo período de consulta: '{}' até '{}'.", data_inicio, data_fim
    )
    ctx.locator("input[name='periodo1']").type(data_inicio, delay=50)
    ctx.locator("input[name='periodo2']").type(data_fim, delay=50)

    # Preenche U.G.
    if not page.locator("select[name='listaUg']"):
        logger.info("Preenchendo código da UG: '{}'.", ug["codigo"])
        preencher_campo(ctx, "input[name='cdUg']", ug["codigo"])

    # Preenche Almoxarifado
    logger.info("Preenchendo sigla do almoxarifado: '{}'.", almoxarifado["sigla"])
    preencher_campo(ctx, "input[name='listAlmoxs']", almoxarifado["sigla"])

    logger.info(
        "Finalizou preenchimento de dados gerais no almoxarifado '{}'.",
        almoxarifado["nome"],
    )
