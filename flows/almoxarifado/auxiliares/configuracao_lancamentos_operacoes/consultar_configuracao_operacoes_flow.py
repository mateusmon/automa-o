from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_configuracao_operacoes(page: Page) -> None:
    logger.info("Iniciou cosulta de Configuração Lançamentos - Operações")

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Preenchendo nome 'AUTOMAÇÃO'.")
    ctx.locator("input[name='model-1']").fill("AUTOMAÇÃO")
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou cosulta de Configuração Lançamentos - Operações")
