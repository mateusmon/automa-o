from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo


def preencher_dados_gerais(page: Page) -> None:
    ctx = escopo(page)

    logger.info("Iniciou preenchimento de dados gerais.")
    
    primeira_linha = ctx.locator("table.tabela tbody tr").first

    for campo in primeira_linha.locator("input[type='text']").all():
        campo.type("1")

    logger.info("Finalizou preenchimento de dados gerais.")
