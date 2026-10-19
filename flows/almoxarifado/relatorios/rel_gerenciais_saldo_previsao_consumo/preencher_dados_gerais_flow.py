from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_almoxarifado
from utils.versao import escopo
from utils.waits import preencher_campo


def preencher_dados_gerais(page: Page, ur: dict[str, str]) -> bool:
    logger.info("Iniciou preenchimento de dados gerais na UR '{}'.", ur["nome"])

    ctx = escopo(page)
    data = obter_data_almoxarifado(page, formato="DDMMYYYY")

    # Preencher U.R
    logger.info("Preenchendo nome da UR: '{}'.", ur["nome"])
    preencher_campo(ctx, "input[name='cdUr']", ur["nome"])

    # Preencher Data do movimento
    logger.info("Preenchendo data do movimento: '{}'.", data)
    ctx.locator("input[name='movimento']").click()
    ctx.locator("input[name='movimento']").type(data, delay=50)

    if ctx.locator("button[name='submitPrint']").is_disabled():
        logger.warning("A impressão do relatório está desabilitada para o cliente.")
        return False

    logger.info("Finalizou preenchimento de dados gerais na UR '{}'.", ur["nome"])
    return True
