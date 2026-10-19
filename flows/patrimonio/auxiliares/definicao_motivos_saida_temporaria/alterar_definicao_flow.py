from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, clicar_com_ajax, esperar_sucesso_ou_erro


def alterar_definicao(page: Page) -> None:
    logger.info("Iniciou o alteração de definição.")

    ctx = escopo(page)

    clicar_com_ajax(ctx, "input[name='inDetalhesRetorno']")
    aguardar_ajax_global(page)
    
    clicar_com_ajax(ctx, "button[name='submitFinish']")
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)
    
    logger.info("Finalizou o alteração de definição.")
