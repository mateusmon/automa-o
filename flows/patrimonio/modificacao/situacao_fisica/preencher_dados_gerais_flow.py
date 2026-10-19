from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def preencher_dados_gerais(page: Page, ug: dict[str, str]) -> None:
    logger.info("Iniciou preenchimento de dados gerais de situação física {}.", ug["codigo"])

    ctx = escopo(page)

    preencher_campo(ctx, "input[name='ug']", ug["codigo"])
    aguardar_ajax_global(page)

    logger.info("Finalizou preenchimento de dados gerais de situação física {}.", ug["codigo"])
