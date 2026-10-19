from loguru import logger
from playwright.sync_api import Page

from navigation.navegar_para_bem import acessar_bem
from utils.espera import aguardar_ajax_global
from utils.versao_gen import escopo


def possui_caracteristica(page: Page) -> bool:
    """
    Retorna true caso o bem já tenha uma característica.
    """
    # Navigation
    acessar_bem(page, True)
    
    ctx = escopo(page)

    # Search
    campo_bem = ctx.locator('textarea[name="complemento_NmBemServico"]')
    campo_bem.clear()
    campo_bem.fill("M01 MESA")
    aguardar_ajax_global(page)
    ctx.locator('button[name="lookup-complemento_NmBemServico"]').click()
    aguardar_ajax_global(page)
    ctx.locator('img[title="Retornar"]').click()
    aguardar_ajax_global(page)
    ctx.locator('button[name="submitTabCaracteristicas"]').click()
    aguardar_ajax_global(page)
    valor = ctx.locator('input[name="caracteristicas-Nome-1-3"]').input_value()
    logger.info(valor)

    return valor != ""
