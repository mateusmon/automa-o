from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import preencher_campo


def preencher_dados_gerais(page: Page, almoxarifado: dict) -> None:
    logger.info("Iniciou preenchimento de dados gerais.")

    ctx = escopo(page)

    logger.info("Preenchendo sigla '{}'.", almoxarifado["sigla"])
    preencher_campo(ctx, "input[name='cdAlmoxarifado']", almoxarifado["sigla"])
    logger.info("Preenchendo nome 'CATÁLOGO DE TESTE AUTOMATIZADO'.")
    ctx.locator("input[name='dsCatalogo']").type("CATÁLOGO DE TESTE AUTOMATIZADO", delay=50)
    logger.info("Preenchendo finalidade 'REQUISITANTES'.")
    preencher_campo(ctx, "input[name='cdTipoCatalogo']", "001")

    logger.info("Finalizou preenchimento de dados gerais.")
