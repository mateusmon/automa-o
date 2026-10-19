from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_almoxarifado
from utils.versao import escopo
from utils.waits import preencher_campo


def preencher_dados_gerais(
    page: Page, ug: dict[str, str], almoxarifado: dict[str, str]
) -> None:
    logger.info(
        "Iniciou preenchimento de dados gerais no almoxarifado '{}'.",
        almoxarifado["nome"],
    )

    ctx = escopo(page)
    competencia = obter_data_almoxarifado(page, formato="YYYYMM")
    ano_atual = competencia[:4]

    # Preenche o período
    logger.info("Preenchendo período inicial: '{}'.", f"{ano_atual}01")
    ctx.locator("input[name='anoMesInicial']").type(f"{ano_atual}01", delay=50)
    logger.info("Preenchendo período final: '{}'.", competencia)
    ctx.locator("input[name='anoMesFinal']").type(competencia, delay=50)

    # Preenche a U.G.
    if not page.locator("select[name='listaUg']"):
        logger.info("Preenchendo código da UG: '{}'.", ug["codigo"])
        preencher_campo(ctx, "input[name='cdUg']", ug["codigo"])

    # Preenche o Almoxarifado
    logger.info("Preenchendo sigla do almoxarifado: '{}'.", almoxarifado["sigla"])
    preencher_campo(ctx, "input[name='cdAlmox']", almoxarifado["sigla"])

    logger.info(
        "Finalizou preenchimento de dados gerais no almoxarifado '{}'.",
        almoxarifado["nome"],
    )
