from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, proximo_nome


def alterar_catalogo(page: Page) -> None:
    logger.info("Iniciou alteração de Catálogo de Materiais.")

    ctx = escopo(page)

    campo = ctx.locator("input[name='dsCatalogo']")

    logger.info("Alterando nome do Catálogo de Materiais: '{}' -> '{}'.", campo.input_value(), proximo_nome(campo.input_value()))
    campo.fill(proximo_nome(campo.input_value()))
    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou alteração de Catálogo de Materiais.")
