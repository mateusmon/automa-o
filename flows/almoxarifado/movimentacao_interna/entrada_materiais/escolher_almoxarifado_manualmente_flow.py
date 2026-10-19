from loguru import logger

from utils.waits import esperar_pagina_carregar


def escolher_almoxarifado_manualmente(page):
    logger.info("Iniciou escolha de almoxarifado manualmente.")

    logger.info("Clicando no botão 'Lookup' para selecionar o almoxarifado.")
    page.locator('button[name="lookup-almoxarifado"]').click()
    esperar_pagina_carregar(page)

    logger.info("Clicando no botão 'Consultar novo registro' para abrir a tela de consulta.")
    page.get_by_title("Consultar novo registro").click()

    esperar_pagina_carregar(page)

    primeira_linha = page.locator('tr[name="searchResultData"][model="model-0"]')
    botao_anexar = primeira_linha.locator('button[name="submitUse"]')

    if botao_anexar.is_visible(): 
        logger.info("Botão 'Anexar' encontrado. Clicando para anexar o almoxarifado.")
        botao_anexar.click()

    esperar_pagina_carregar(page)

    logger.info("Finalizou escolha de almoxarifado manualmente.")