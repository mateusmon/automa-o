from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def validar_botoes_comuns(page: Page):

    ctx = escopo(page)

    # Botões de + linhas e - linhas
    logger.info("Validando botões de 'Adicionar' e 'Remover' linhas.")
    ctx.locator("button[name='submitAddLine1']").click()
    aguardar_ajax_global(page)
    ctx.locator("button[name='submitPurgeLine1']").click()
    aguardar_ajax_global(page)

    # Botão de Consulta e retornar a página
    logger.info("Validando botão de 'Consulta' e 'Retornar' à página.")
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)
    ctx.locator("button[name='submitCancel']").click()
    aguardar_ajax_global(page)

    # Botão de Visualizar e retornar a página
    logger.info("Validando botão de 'Visualizar' e 'Retornar' à página.")
    ctx.locator("button[name='submitView']").click()
    aguardar_ajax_global(page)
    ctx.locator("button[name='submitBack']").click()
    aguardar_ajax_global(page)

    # Confirmar Transferencia
    logger.info("Validando botão de 'Confirmar' transferência.")
    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)
