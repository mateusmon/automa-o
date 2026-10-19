from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro

def preencher_dados_gerais(page: Page, nome: str = "OBSERVAÇÃO TESTE"):
    logger.info("Preenchendo dados gerais da observação com o nome '{}'.", nome)

    ctx = escopo(page)

    # Preenche Nome da observação
    logger.info("Preenchendo nome da observação: '{}'.", nome)
    ctx.locator("input[name='nmTpObs']").fill(nome)
    
    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)

    esperar_sucesso_ou_erro(ctx)

    logger.info("Dados gerais da observação com o nome '{}' preenchidos.", nome)