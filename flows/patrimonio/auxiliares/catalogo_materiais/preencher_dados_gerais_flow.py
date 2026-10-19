from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import preencher_campo, aguardar_ajax_global


def preencher_dados_gerais(page: Page, ug: dict, ds_catalogo: str) -> None:
    logger.info("Iniciou preenchimento de dados gerais do Catálogo de Materiais '{}' na UG '{}'.", ds_catalogo, ug["nome"])

    ctx = escopo(page)

    aguardar_ajax_global(page)

    logger.info("Preenchendo código da UG: '{}'.", ug["codigo"])
    preencher_campo(ctx, "input[name='cdUg']", ug["codigo"])
    logger.info("Preenchendo nome do Catálogo de Materiais: '{}'.", ds_catalogo)
    ctx.locator("input[name='dsCatalogo']").fill(ds_catalogo)
    logger.info("Preenchendo primeiro tipo do Catálogo de Materiais.")
    preencher_campo(ctx, "input[name='cdTipoCatalogo']", "   ")

    logger.info("Finalizou preenchimento de dados gerais do Catálogo de Materiais '{}' na UG '{}'.", ds_catalogo, ug["nome"])
