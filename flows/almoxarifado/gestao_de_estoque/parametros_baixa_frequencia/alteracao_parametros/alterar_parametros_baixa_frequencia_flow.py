from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def alterar_estoque_base(page: Page) -> None:
    logger.info("Iniciou alteração de estoque base.")

    ctx = escopo(page)

    campo = ctx.locator("input[name='qtEstoqueBase-1-5']")

    if campo.input_value() == "35":
        valor = "30"
    else:
        valor = "35"

    logger.info("Alterando valor do estoque base: '{}' -> '{}'.", campo.input_value(), valor)
    campo.fill(valor)

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou alteração de estoque base.")
