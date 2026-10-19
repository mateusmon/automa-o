from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_roteiro_padrao_baixa(page: Page) -> None:
    logger.info("Iniciou consulta de Roteiro Padrão para Baixa.")

    ctx = escopo(page)
    
    ctx.click("button[name='submitSearch']")
    aguardar_ajax_global(page)

    logger.info("Preenchendo Roteiro Padrão para Baixa: 'ROTEIRO DE BAIXA'.")
    ctx.fill("input[name='model-1']", "ROTEIRO DE BAIXA")

    ctx.click("button[name='submitSearch']")
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de Roteiro Padrão para Baixa.")
