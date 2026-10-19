from playwright.sync_api import Page
from loguru import logger
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def preencher_dados_gerais(page: Page, nome: str):
    logger.info("Iniciou preenchimento de dados gerais de Situação Física: '{}'.", nome)

    ctx = escopo(page)

    aguardar_ajax_global(page)

    logger.info("Preenchendo nome da Situação Física: '{}'.", nome)
    ctx.locator('input[name="nmTpSitFisica"]').fill(nome)
    ctx.locator('button[name="submitFinish"]').click()

    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou preenchimento de dados gerais de Situação Física: '{}'.", nome)