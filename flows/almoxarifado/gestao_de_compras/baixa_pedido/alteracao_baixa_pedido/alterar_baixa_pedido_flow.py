from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro

def alterar_baixa_pedido(page: Page)->None:
    logger.info("Alterando baixa de pedido.")

    ctx = escopo(page)

    campo = ctx.locator("input[name='qtABaixar-1-6']")
    quantidade_atendida = ctx.locator("td[name='qtAtendida-1-5']").inner_text()

    if quantidade_atendida == "0":
        valor = "1"
    else:
        valor = "0"

    logger.info("Alterando quantidade atendida: '{}' -> '{}'.", quantidade_atendida, valor)
    campo.fill(valor)

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Baixa de pedido alterado.")