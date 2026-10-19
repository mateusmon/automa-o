from datetime import datetime

from dateutil.relativedelta import relativedelta
from loguru import logger
from playwright.sync_api import Page

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
    data_fim = datetime.today().strftime("%d%m%Y")
    data_inicio = (datetime.today() - relativedelta(months=6)).strftime("%d%m%Y")

    # Preenche Data
    logger.info(
        "Preenchendo período de consulta: '{}' até '{}'.", data_inicio, data_fim
    )
    ctx.locator("input[name='dataInicial']").type(data_inicio, delay=50)
    ctx.locator("input[name='dataFinal']").type(data_fim, delay=50)

    # Preenche U.G.
    logger.info("Preenchendo código da UG: '{}'.", ug["codigo"])
    preencher_campo(ctx, "input[name='ug']", ug["codigo"])

    # Preenche Almoxarifado
    logger.info("Preenchendo sigla do almoxarifado: '{}'.", almoxarifado["sigla"])
    preencher_campo(ctx, "input[name='almoxarifado']", almoxarifado["sigla"])

    logger.info(
        "Finalizou preenchimento de dados gerais no almoxarifado '{}'.",
        almoxarifado["nome"],
    )
