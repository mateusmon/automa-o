from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def preencher_dados_gerais(page: Page, ua: dict[str, str]) -> None:
    logger.info("Iniciou preenchimento de dados gerais da modificação de responsável do local {}.", ua["sigla"])

    ctx = escopo(page)
    preencher_campo(ctx, "input[name='ua']", ua["sigla"])
    aguardar_ajax_global(page)

    logger.info("Finalizou preenchimento de dados gerais da modificação de responsável do local {}.", ua["sigla"])
