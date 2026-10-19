from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, proximo_nome


def alterar_descricao(page: Page) -> None:
    logger.info("Iniciou alteração de inventário.")

    ctx = escopo(page)

    campo = ctx.locator("textarea[name='dsFinalidade']")
    logger.info("Alterando descrição de inventário: '{}' -> '{}'.", campo.input_value(), proximo_nome(campo.input_value()))
    campo.fill(proximo_nome(campo.input_value()))
    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou alteração de inventário.")
