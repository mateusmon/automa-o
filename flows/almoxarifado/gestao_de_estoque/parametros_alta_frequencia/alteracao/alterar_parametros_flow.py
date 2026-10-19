from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def alterar_parametros(page: Page) -> None:
    logger.info("Iniciou alteração de Política de Compras de Alta Frequência.")

    ctx = escopo(page)

    campo_valor_c = ctx.locator("input[name='pcValor-3-2']")
    campo_valor_nc = ctx.locator("input[name='pcValor-4-2']")

    if campo_valor_c.input_value() == "5":
        logger.info("Alterando valores de Política de Compras de Alta Frequência: '5' -> '6' e '5' -> '4'.")
        campo_valor_c.fill("6")
        campo_valor_nc.fill("4")
    else:
        logger.info("Alterando valores de Política de Compras de Alta Frequência: '{}' -> '5' e '{}' -> '5'.", campo_valor_c.input_value(), campo_valor_nc.input_value())
        campo_valor_c.fill("5")
        campo_valor_nc.fill("5")

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou alteração de Política de Compras de Alta Frequência.")
