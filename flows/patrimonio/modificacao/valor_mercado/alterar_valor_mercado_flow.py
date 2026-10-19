from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def alterar_valor_mercado(page: Page, desfazer: bool = False) -> None:
    ctx = escopo(page)
    logger.info("Iniciou alteração de valor do mercado do bem {}.", ctx.locator("input[name='itens-1-6']").input_value())

    campo = ctx.locator("input[name='itens-1-6']")

    valor = campo.input_value().replace(".", "").replace(",", ".")

    if desfazer:
        # Valor 10% menor
        valor_alterado = float(valor) / 1.1
    else:
        # Valor 10% maior
        valor_alterado = float(valor) * 1.1

    valor_str = f"{valor_alterado:.2f}".replace(".", ",")

    logger.info("Alterando valor do mercado do bem {} para '{}'.", ctx.locator("input[name='itens-1-6']").input_value(), valor_str)
    campo.fill(valor_str)
    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou alteração de valor do mercado do bem {}.", ctx.locator("input[name='itens-1-6']").input_value())
