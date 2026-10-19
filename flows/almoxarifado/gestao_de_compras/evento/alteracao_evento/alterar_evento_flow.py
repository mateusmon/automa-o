from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, proximo_nome

def alterar_evento(page: Page):
    logger.info("Alterando evento.")

    ctx = escopo(page)

    campo = ctx.locator("input[name='dsPrevisaoCons']")
    logger.info("Alterando descrição do evento: '{}' -> '{}'.", campo.input_value(), proximo_nome(campo.input_value()))
    campo.fill(proximo_nome(campo.input_value()))

    aguardar_ajax_global(page)

    ctx.locator("button[name='submitFinish']").click()

    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Evento alterado.")