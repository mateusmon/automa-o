from loguru import logger
from playwright.sync_api import Page

from utils.waits import esperar_pagina_carregar

def excluir_relatorios(page: Page) -> None:
    logger.info("Excluindo relatórios.")

    page.locator("input[name='submitMarkAll1']").check()
    page.locator("button[name='submitFinish']").click()
    esperar_pagina_carregar(page)

    logger.info("Relatórios excluidos.")