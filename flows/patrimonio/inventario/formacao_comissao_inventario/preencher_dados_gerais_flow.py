from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def preencher_dados_gerais(page: Page, ug_data: dict[str, str]) -> None:
    logger.info("Iniciou o preenchimento dos dados gerais.")

    ctx = escopo(page)

    preencher_campo(ctx, "input[name='ug']", ug_data["codigo"])

    logger.info("Preenchendo campo de Nome da Comissão com valor fixo 'COMISSAO DE INVENTARIO'.")
    ctx.locator("input[name='nmComissao']").fill("COMISSAO DE INVENTARIO")
    aguardar_ajax_global(page)

    logger.info("Finalizou o preenchimento dos dados gerais .")
