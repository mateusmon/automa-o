
from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_almoxarifado
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def preencher_dados_gerais(page: Page, nome: str = "UM GRANDE EVENTO") -> None:
    logger.info("Preenchendo dados gerais do evento.")

    ctx = escopo(page)

    data_hoje = obter_data_almoxarifado(page, "DDMMYYYY")

    page.mouse.move(0, 0)
    
    ctx.locator("input[name='dtInicio']").click()
    logger.info("Preenchendo data de início do evento '{}'.", data_hoje)
    ctx.locator("input[name='dtInicio']").type(data_hoje, delay=50)
    logger.info("Preenchendo data de término do evento '{}'.", data_hoje)
    ctx.locator("input[name='dtFinal']").type(data_hoje, delay=50)
    logger.info("Preenchendo descrição do evento '{}'.", nome)
    ctx.locator("input[name='dsPrevisaoCons']").type(nome)
    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Preenchimento de dados gerais do evento finalizado.")
