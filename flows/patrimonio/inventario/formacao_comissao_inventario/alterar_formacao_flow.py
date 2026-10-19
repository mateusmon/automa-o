from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro
from utils.geradores import gerar_numero_com_digitos


def alterar_formacao(page: Page) -> None:
    logger.info("Iniciou alteração de comissão de inventário.")

    ctx = escopo(page)

    logger.info("Preenchendo campo de Número do Processo com valor gerado aleatoriamente '{}'.", gerar_numero_com_digitos(10))
    ctx.locator("input[name='nrProcesso']").fill(gerar_numero_com_digitos(10))
    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou alteração de comissão de inventário.")
