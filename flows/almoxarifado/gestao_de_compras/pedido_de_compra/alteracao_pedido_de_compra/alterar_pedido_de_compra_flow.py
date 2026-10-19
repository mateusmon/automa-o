from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, proximo_nome


def alterar_pedido_compra(page: Page) -> None:
    logger.info("Alterando pedido de compra.")

    ctx = escopo(page)

    campo = ctx.locator("textarea[name='dsJustificativa']")
    logger.info("Alterando justificativa do pedido de compra: '{}' -> '{}'.", campo.input_value(), proximo_nome(campo.input_value()))
    campo.fill(proximo_nome(campo.input_value()))

    aguardar_ajax_global(page)

    ctx.locator("button[name='submitFinish']").click()

    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Pedido de compra alterado.")
