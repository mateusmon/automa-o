from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro

def preencher_dados_gerais(page: Page, nome: str = "DOCUMENTO TESTE", tamanho: str = "20"):
    logger.info("Preenchendo dados gerais do documento '{}' .", nome)

    ctx = escopo(page)

    ctx.locator("button[name='submitCancel']").click()
    aguardar_ajax_global(page)

    # Preenche Nome do documento
    logger.info("Preenchendo nome do documento: '{}'.", nome)
    ctx.locator("input[name='nmTpDocumento']").fill(nome)

    # Preenche Tamanho do documento
    logger.info("Preenchendo tamanho do documento: '{}'.", tamanho)
    ctx.locator("input[name='nrTamanho']").fill(tamanho)

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    
    esperar_sucesso_ou_erro(ctx)

    logger.info("Dados gerais do documento '{}' preenchidos.", nome)