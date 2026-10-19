from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_configuracao_observacao(page: Page) -> None:
    logger.info("Iniciou consulta de Configuração Lançamentos - Tipo de Observação.")

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Consultando nome 'AUTOMAÇÃO'.")
    ctx.locator("input[name='model-1']").fill("AUTOMAÇÃO")
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de Configuração Lançamentos - Tipo de Observação.")
