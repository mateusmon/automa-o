from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import preencher_campo


def preencher_dados_gerais(page: Page, ug: dict[str, str]) -> None:
    logger.info("Iniciou o preenchimento dos dados gerais de seleção de bens com a UG: '{}'.", ug["codigo"])

    ctx = escopo(page)

    preencher_campo(ctx, "input[name='ug']", ug["codigo"])
    ctx.locator("input[name='dsObjetivo']").type("AUTOMATIZAÇÃO", delay=50)
    
    logger.info("Finalizou o preenchimento dos dados gerais de seleção de bens com a UG: '{}'.", ug["codigo"])
