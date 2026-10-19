from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, clicar_com_ajax, esperar_sucesso_ou_erro, proximo_nome


def alterar_roteiro_padrao_baixa(page: Page) -> None:
    logger.info("Iniciou alteração de Roteiro Padrão para Baixa.")

    ctx = escopo(page)

    campo = ctx.locator("input[name='tarefas-1-3']")

    logger.info("Alterando nome do Roteiro Padrão para Baixa: '{}' -> '{}'.", campo.input_value(), proximo_nome(campo.input_value()))
    campo.fill(proximo_nome(campo.input_value()))

    clicar_com_ajax(ctx, "button[name='submitFinish']")
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou alteração de Roteiro Padrão para Baixa.")
