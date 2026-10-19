from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro

def alterar_caracteristica(page: Page):
    logger.info("Alterando Característica.")

    ctx = escopo(page)

    campo = ctx.locator("input[name='nrTamanho']")

    if campo.input_value() == "50":
        tamanho = "100"
    else:
        tamanho = "50"

    logger.info("Alterando tamanho: '{}' -> '{}'.", campo.input_value(), tamanho)
    ctx.locator("input[name='nrTamanho']").fill(tamanho)
    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Característica alterada.")