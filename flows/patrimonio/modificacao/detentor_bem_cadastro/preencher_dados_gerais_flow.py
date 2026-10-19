from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def preencher_dados_gerais(page: Page, ug_data: dict[str, str], funcionario: dict[str, str]) -> None:
    logger.info("Iniciou o preenchimento dos dados gerais do detentor do bem {}.", funcionario["nome"])

    ctx = escopo(page)

    preencher_campo(ctx, "input[name='ug']", ug_data["codigo"])
    preencher_campo(ctx, "input[name='cdDetentorD']", funcionario["nome"])
    ctx.locator("input[name='inAssinatura'][value='S']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou o preenchimento dos dados gerais do detentor do bem {}.", funcionario["nome"])
