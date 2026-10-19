from playwright.sync_api import Page
from loguru import logger

from utils.waits import esperar_pagina_carregar


def pular_impressao(page: Page) -> None:
    logger.info("Pulando impressão.")

    page.locator("button[name='submitBack']").click()
    esperar_pagina_carregar(page)
