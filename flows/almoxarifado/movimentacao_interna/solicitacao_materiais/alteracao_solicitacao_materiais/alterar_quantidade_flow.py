from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def alterar_quantidade(page: Page) -> None:
    logger.info("Iniciou alteração de solicitação de materiais.")

    ctx = escopo(page)

    quantidade_atual = ctx.locator("input[name='qtSolicitacao1-5']").input_value()

    if quantidade_atual == "2":
        nova_quantidade = "1"
    else:
        nova_quantidade = "2"

    logger.info(
        "Alterando quantidade: '{}' -> '{}'.", quantidade_atual, nova_quantidade
    )
    ctx.locator("input[name='qtSolicitacao1-5']").click()
    ctx.locator("input[name='qtSolicitacao1-5']").fill(nova_quantidade)
    aguardar_ajax_global(page)

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou alteração de solicitação de materiais.")
