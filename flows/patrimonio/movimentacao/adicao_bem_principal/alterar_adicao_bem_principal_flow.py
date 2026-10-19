from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def alterar_adicao_bem_principal(page: Page) -> None:
    logger.info("Alterando adição de Bem Principal.")
    
    ctx = escopo(page)
    
    ctx.locator("button[name='submitConfirm']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Adição a Bem Principal alterado.")