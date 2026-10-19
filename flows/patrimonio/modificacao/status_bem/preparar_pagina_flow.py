from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def preparar_pagina(page: Page) -> None:
    logger.info("Iniciou preparação de página.")

    ctx = escopo(page)
    ctx.locator("button[name='submitNew']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou preparação de página.")
