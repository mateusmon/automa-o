from playwright.sync_api import expect, Page
from loguru import logger
from utils.waits import esperar_pagina_carregar


def excluir_relatorios(page: Page) -> None:
    logger.info("Iniciando exclusão de relatórios.")

    # Selecionando a caixa excluir todos
    page.locator('input[name="submitMarkAll1"]').click()

    # Esperando até todos serem selecionados
    #expect(page.locator('input[name="deletable-1-1"]')).to_be_checked()
    esperar_pagina_carregar(page)

    # Clicando no botão para excluir
    page.locator('button[name="submitFinish"]').click()

    esperar_pagina_carregar(page)

    logger.info("Finalizando exclusão de relatórios.")
