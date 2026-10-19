from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, clicar_com_ajax, preencher_campo


def preencher_endereco(page: Page, material: dict) -> None:
    endereco = material["codigo_endereco"]

    logger.info("Iniciou preenchimento de endereço do material '{}'.", material["nome"])

    ctx = escopo(page)

    logger.info("Preenchendo endereço '{}'.", endereco)
    preencher_campo(ctx, "input[name='endereco']", endereco)
    clicar_com_ajax(ctx,"button[name='submitSearch']")
    aguardar_ajax_global(page)

    logger.info("Finalizou preenchimento de endereço do material '{}'.", material["nome"])
