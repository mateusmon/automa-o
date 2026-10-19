from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def alterar_cadastro_previsao(page: Page) -> None:
    logger.info("Iniciou alteração de cadastro de previsão de consumo de UR.")

    ctx = escopo(page)
    
    # Alterando a quantidade
    campo = ctx.locator("input[name='qtPrevRequisicao-2-7']")

    if campo.input_value() == "1":
        valor = "2"
    else:
        valor = "1"

    logger.info("Alterando quantidade de previsão de consumo: '{}' -> '{}'.", campo.input_value(), valor)
    campo.fill(valor)

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou alteração de cadastro de previsão de consumo de UR.")
