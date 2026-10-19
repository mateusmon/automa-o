from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, proximo_nome


def alterar_configuracao(page: Page) -> None:
    logger.info("Iniciou alteração de Configuração de Lançamentos - Operações.")

    ctx = escopo(page)

    campo = ctx.locator("input[name='sgTipoMovimento']")

    nome_atual = campo.input_value()
    novo_nome = proximo_nome(nome_atual)

    logger.info("Alterando tipo de documento: '{}' -> '{}'.", nome_atual, novo_nome)

    campo.fill(novo_nome)

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou alteração de Configuração de Lançamentos - Operações.")
