from loguru import logger
from playwright.sync_api import Page

from utils.waits import esperar_pagina_carregar, esperar_sucesso_ou_erro

def excluir_documentacoa(page: Page, nome: str = "DOCUMENTO TESTE"):
    logger.info("Excluindo documentação de nome '{}'.", nome)

    page.locator("button[name='submitSearch']").click()

    esperar_pagina_carregar(page)

    # Preencher o nome do tipo de documento
    page.locator("input[name='model-1']").click()
    page.locator("input[name='model-1']").fill(nome)

    page.locator("button[name='submitSearch']").click()
    esperar_pagina_carregar(page)

    linha = page.locator("table[name='paginationTable'] tbody tr").filter(
        has=page.locator("td").nth(1).filter(
            has_text=nome
        )
    ).first

    if linha.count() == 0:
        logger.info("Nenhum documento de nome '{}' encontrado.", nome)

    linha.locator("button[name='submitUse']").click()
    esperar_pagina_carregar(page)

    # Aceitando caixa de diálogo para confirmação de exclusão
    page.once("dialog", lambda dialog: dialog.accept())
    page.locator("button[name='submitDelete']").click()

    esperar_pagina_carregar(page)
    esperar_sucesso_ou_erro(page)