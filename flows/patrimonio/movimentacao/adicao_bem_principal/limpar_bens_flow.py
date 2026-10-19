from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_patrimonio
from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def limpar_bens(page: Page) -> None:
    logger.info("Iniciou limpeza de bens.")

    ctx = escopo(page)

    aguardar_ajax_global(page)

    botao_retornar = ctx.locator("button[name='submitBack']")

    if botao_retornar.is_visible():
        botao_retornar.click()
        aguardar_ajax_global(page)

    ctx.locator("button[name='submitRestore']").click()
    aguardar_ajax_global(page)

    ctx.locator("input[name='submitMarkAll1']").check()
    aguardar_ajax_global(page)

    data = obter_data_patrimonio(page, formato="DD/MM/YYYY")
    logger.info("Data de Patrimônio obtida: {}", data)

    for linha in ctx.locator(".tabelaComRolagem tbody tr").all():
        patrimonio = linha.locator("input[name^='cdBemPerm']")
        campo_data = linha.locator("input[name^='dtHistorico']")

        if patrimonio.input_value().strip() and campo_data.is_enabled():
            campo_data.fill(data)

    ctx.locator("button[name='submitConfirm']").click()
    aguardar_ajax_global(page)

    ctx.locator("button[name='submitBack']").click()
    aguardar_ajax_global(page)

    ctx.locator("button[name='submitRestore']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou limpeza de bens.")
