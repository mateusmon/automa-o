from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def preencher_dados_gerais_regiao(page: Page, regiao: dict) -> None:
    """
    Preenche a Região e confirma. Cenário A.
    Campos: Código (`cdRegiao`, editável = chave única) e Nome (`nmRegiao`).
    Região superior é opcional e não é preenchida.

    :param regiao: dict do blueprint (codigo, nome).
    """
    logger.info("Iniciou preenchimento de dados gerais de Região '{}'.", regiao["nome"])
 
    ctx = escopo(page)

    aguardar_ajax_global(page)
    ctx.locator("input[name='cdRegiao']").wait_for(state="visible")
    logger.info("Preenchendo Código de Região: '{}'.", regiao["codigo"])
    ctx.locator("input[name='cdRegiao']").fill(regiao["codigo"])
    logger.info("Preenchendo Nome de Região: '{}'.", regiao["nome"])
    ctx.locator("input[name='nmRegiao']").fill(regiao["nome"])

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou preenchimento de dados gerais de Região '{}'.", regiao["nome"])
