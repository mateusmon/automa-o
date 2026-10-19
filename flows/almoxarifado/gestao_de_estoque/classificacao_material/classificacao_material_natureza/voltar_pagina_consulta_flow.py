from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def voltar_pagina_consulta(page: Page) -> None:
    logger.info("Iniciou retorno para página de consulta.")

    ctx = escopo(page)

    ctx.locator("button[name='submitTabConsulta']").click()
    aguardar_ajax_global(page)

    ctx.locator("button[name='submitRestore']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou retorno para página de consulta.")
