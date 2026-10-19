from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def remover_dados_caracteristicas(page: Page) -> bool:
    logger.info("Inicou remoção de dados da característica.")

    ctx = escopo(page)

    delete_checkbox = ctx.locator("input[name='deletable-1-1']")

    if delete_checkbox.count() == 0:
        logger.info("Nenhum dado da característica encontrado. Rode o teste de manutenção de características primeiro.")
        return False
    
    ctx.click("input[name='deletable-1-1']")
    ctx.click("button[name='submitFinish']")
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou remoção de dados da característica.")
    return True