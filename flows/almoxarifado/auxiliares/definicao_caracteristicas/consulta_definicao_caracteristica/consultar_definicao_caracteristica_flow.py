from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global

def consultar_definicao_caracteristica(page: Page, nome: str) -> bool:
    logger.info("Iniciou consulta da Definição de Característica com o nome '{}'.", nome)

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Consultando nome '{}'.", nome)
    ctx.locator("input[name='model-1']").click()
    ctx.locator("input[name='model-1']").type(nome, delay=50)
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    linha = ctx.locator("table[name='paginationTable'] tbody tr")

    if linha.count() == 0:
        logger.info("Nenhuma Característica com o nome '{}' encontrada.", nome)
        return False
    
    linha.locator("button[name='submitUse']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta da Definição de Característica com o nome '{}'.", nome)

    return True