from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def preencher_dados_gerais_funcao(page: Page, funcao: dict) -> None:
    """
    Preenche a Função e confirma. Cenário A (só muda o escopo via `escopo(page)`).
    Campo único: Nome (`nmTpFuncaoHier`); o Código é gerado pelo sistema.

    :param funcao: dict do blueprint (nome).
    """
    logger.info("Iniciou preenchimento de dados gerais de Função '{}'.", funcao["nome"])

    ctx = escopo(page)

    aguardar_ajax_global(page)
    ctx.locator("input[name='nmTpFuncaoHier']").wait_for(state="visible")

    logger.info("Preenchendo campo de Nome de Função com '{}'.", funcao["nome"])
    ctx.locator("input[name='nmTpFuncaoHier']").fill(funcao["nome"])

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou preenchimento de dados gerais de Função '{}'.", funcao["nome"])
