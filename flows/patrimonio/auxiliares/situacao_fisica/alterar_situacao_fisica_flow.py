from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, clicar_com_ajax, esperar_sucesso_ou_erro, proximo_nome


def alterar_situacao_fisica(page: Page) -> None:
    logger.info("Iniciou alteração de Situação Física.")

    ctx = escopo(page)

    campo = ctx.locator("textarea[name='dsTpSitFisica']")

    logger.info("Alterando Situação Física: '{}' -> '{}'.", campo.input_value(), proximo_nome(campo.input_value()))
    campo.fill(proximo_nome(campo.input_value()))
    clicar_com_ajax(ctx, "button[name='submitFinish']")
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou alteração de Situação Física.")
