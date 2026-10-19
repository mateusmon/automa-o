from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global



def validar_botoes_comuns_recarregar(page: Page):

    ctx = escopo(page)

    # Botão de Restaurar
    logger.info("Validando botão de 'Restaurar'.")
    ctx.locator("button[name='submitRestore']").click()
    aguardar_ajax_global(page)

    # Botão de Novo
    logger.info("Validando botão de 'Novo'.")
    ctx.locator("button[name='submitNew']").click()
    aguardar_ajax_global(page)
