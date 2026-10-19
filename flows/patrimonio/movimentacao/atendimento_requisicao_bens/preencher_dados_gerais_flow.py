from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import preencher_campo


def preencher_dados_gerais(page: Page, ug_data: dict[str, str]) -> None:
    logger.info("Iniciou o preenchimento dos dados gerais para a UG '{}'.", ug_data["codigo"])

    ctx = escopo(page)

    preencher_campo(ctx, "input[name='ug']", ug_data["codigo"])
    
    logger.info("Finalizou o preenchimento dos dados gerais para a UG '{}'.", ug_data["codigo"])
