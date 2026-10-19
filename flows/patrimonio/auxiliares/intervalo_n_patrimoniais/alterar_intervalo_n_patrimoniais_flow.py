from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def alterar_intervalo_n_patrimoniais(page: Page) -> None:
    """
    Esta função faz uma alteração simples, alterando o intervalo de 1 para 2 ou 2 para 1.
    """
    logger.info("Iniciou alteração de Intervalo de Nº Patrimoniais.")

    ctx = escopo(page)

    tabela = ctx.locator("table.tabela").first
    linha_controlado = tabela.locator("tbody tr").filter(
        has=ctx.locator("td", has_text="CONTROLADO")
    )
    valor_input = linha_controlado.locator("input[bind='nrInicio']").input_value()

    if valor_input == "1":
        logger.info("Alterando intervalo de Nº Patrimoniais: '1' -> '2'.")
        linha_controlado.locator("td input[bind='nrInicio']").fill("2")
    else:
        logger.info("Alterando intervalo de Nº Patrimoniais: '2' -> '1'.")
        linha_controlado.locator("td input[bind='nrInicio']").fill("1")
    
    ctx.click("button[name='submitFinish']")
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou alteração de Intervalo de Nº Patrimoniais.")
