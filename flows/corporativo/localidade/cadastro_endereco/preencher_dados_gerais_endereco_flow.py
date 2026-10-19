from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo


def preencher_dados_gerais_endereco(page: Page, endereco: dict) -> None:
    """
    Preenche o Endereço e confirma. Cenário A.
    Campos: Nome (`nmLocal`) e Instalação (`instalacao`, lookup). Local superior é
    opcional. Órgão pré-preenchido (varia por cliente) e Código gerado.

    :param endereco: dict do blueprint (nome, instalacao).
    """
    logger.info("Iniciou preenchimento de dados gerais de Endereço '{}'.", endereco["nome"])

    ctx = escopo(page)

    aguardar_ajax_global(page)
    ctx.locator("input[name='nmLocal']").wait_for(state="visible")
    logger.info("Preenchendo Nome de Endereço: '{}'.", endereco["nome"])
    ctx.locator("input[name='nmLocal']").fill(endereco["nome"])
    preencher_campo(ctx, "input[name='instalacao']", endereco["instalacao"])

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou preenchimento de dados gerais de Endereço '{}'.", endereco["nome"])
