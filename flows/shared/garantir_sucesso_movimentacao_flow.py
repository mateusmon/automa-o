from loguru import logger

from utils.waits import esperar_pagina_carregar


def garantir_sucesso_movimentacao(page):
    logger.info("Verificando resultado do cadastro.")

    info = page.locator('div[name="divInfoMsg"]')
    error = page.locator('div[name="divErrorMsg"]')

    result = info.or_(error).first
    result.wait_for(state="visible")

    esperar_pagina_carregar(page)

    if info.count() > 0 and info.first.is_visible():
        logger.info("Requisição cadastrada com sucesso.")
        return True

    if error.count() > 0 and error.first.is_visible():
        logger.error("Erro ao cadastrar requisição.")
        return False
