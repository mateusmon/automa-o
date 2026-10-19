from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import preencher_campo


def consultar_intervalo_n_patrimoniais(page: Page, ug: dict[str, str]) -> None:
    logger.info("Iniciou consulta de Intervalo de Nº Patrimoniais na UG '{}'.", ug["nome"])

    ctx = escopo(page)

    logger.info("Preenchendo código da UG: '{}'.", ug["codigo"])
    preencher_campo(ctx, "input[name='ug']", ug["codigo"])

    logger.info("Finalizou consulta de Intervalo de Nº Patrimoniais na UG '{}'.", ug["nome"])
