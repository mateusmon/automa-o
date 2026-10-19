from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, clicar_com_ajax, esperar_sucesso_ou_erro

def alterar_observacao(page: Page):
    logger.info("Alterando observação.")

    ctx = escopo(page)

    clicar_com_ajax(ctx, "input[name='bloqueado']")

    clicar_com_ajax(ctx, "button[name='submitFinish']")
    aguardar_ajax_global(page)

    esperar_sucesso_ou_erro(ctx)
    
    logger.info("Observação alterada.")