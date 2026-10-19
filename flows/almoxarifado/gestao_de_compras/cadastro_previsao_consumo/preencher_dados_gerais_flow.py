from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_almoxarifado
from utils.versao import escopo
from utils.waits import preencher_campo


def preencher_dados_gerais(page: Page, ur_data: dict) -> None:
    logger.info("Preenchendo dados do gerais do cadastro de previsão de consumo da UR {}.", ur_data["nome"])

    ctx = escopo(page)

    # A linha de validade está disponível em alguns clientes
    linha_validade = ctx.locator("li[name='divValidade']")
    if linha_validade.is_visible():

        ano_atual = obter_data_almoxarifado(page, "YYYY/MM").split("/")[0]

        # Números de data são escritos sem barra porque o site coloca a barra automaticamente
        inicio = f"0101{ano_atual}"
        fim = f"3112{ano_atual}"

        logger.info("Preenchendo período de validade: {} a {}.", inicio, fim)
        ctx.locator("input[name='dtInicio']").type(inicio, delay=50)
        ctx.locator("input[name='dtFinal']").type(fim, delay=50)

    logger.info("Preenchendo descrição da previsão de consumo 'PREVISÃO DE CONSUMO ANUAL'.")
    ctx.locator("input[name='dsPrevisaoCons']").type("PREVISÃO DE CONSUMO ANUAL", delay=50)

    logger.info("Preenchendo UR '{}'.", ur_data["nome"])
    preencher_campo(ctx, "input[name='ur']", ur_data["nome"])

    logger.info("Preenchimento de dados gerais do cadastro de previsão de consumo da UR {} finalizado.", ur_data["nome"])
