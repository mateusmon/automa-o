from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, proximo_nome


def alterar_catalogo_restrito(page: Page) -> None:
    logger.info("Iniciou alteração de catálogo restrito.")

    ctx = escopo(page)

    campo = ctx.locator("input[name='dsCatalogo']")

    valor_atual = campo.input_value()
    novo_valor = proximo_nome(valor_atual)

    logger.info("Alterando valor: '{}' -> '{}'.", valor_atual, novo_valor)
    
    # Preenche o input com o novo valor
    campo.fill(novo_valor)

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou alteração de catálogo restrito.")
