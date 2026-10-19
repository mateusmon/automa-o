from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import esperar_sucesso_ou_erro



def preencher_dados_gerais(page: Page, nome: str = "DOCUMENTO AUTOMAÇÃO", tamanho: str = "10") -> None:
    logger.info("Preenchendo dados gerais.")

    ctx = escopo(page)

    # Preenche o nome da característica
    logger.info("Preenchendo nome '{}'.", nome)
    ctx.locator("input[name='nmTpDocumento']").click()
    ctx.locator("input[name='nmTpDocumento']").fill(nome)

    # Preenche o tamanho
    logger.info("Preenchendo tamanho '{}'.", tamanho)
    ctx.locator("input[name='nrTamanho']").click()
    ctx.locator("input[name='nrTamanho']").fill(tamanho)

    ctx.locator("button[name='submitFinish']").click()

    esperar_sucesso_ou_erro(ctx)

    logger.info("Preenchimento de dados gerais finalizado.")
