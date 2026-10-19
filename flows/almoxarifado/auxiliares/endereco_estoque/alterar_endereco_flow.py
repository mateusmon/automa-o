from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, proximo_nome


def alterar_endereco(page: Page) -> None:
    logger.info("Iniciou alteração de endereço de estoque.")

    ctx = escopo(page)

    sigla_input = ctx.locator("input[name='sgEnderecoEst']")

    sigla_atual = sigla_input.input_value()
    nova_sigla = proximo_nome(sigla_atual)

    logger.info("Alterando sigla do endereço de estoque: '{}' -> '{}'.", sigla_atual, nova_sigla)

    sigla_input.fill(nova_sigla)

    ctx.click("button[name='submitFinish']")
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou alteração de endereço de estoque.")
