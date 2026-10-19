from loguru import logger
from playwright.sync_api import Page

from utils.waits import esperar_pagina_carregar

def verificar_existencia_endereco(page: Page, almoxarifado: dict[str,str,], material: dict[str, str], endereco: dict[str, str]):
    logger.info("Iniciou verificação de existência de endereços para o material {}.", material["nome"])

    descricao_endereco = endereco["descricao"]
    nome_completo_material = f"{material["nome"]} {material["complemento"]}"

    page.locator("button[name='submitSearch']").click()
    esperar_pagina_carregar(page)

    logger.info("Preenchendo sigla do almoxarifado '{}'.", almoxarifado["sigla"])
    page.locator("input[name='model-0']").fill(almoxarifado["sigla"])
    page.locator("button[name='lookup-model-0']").click()

    logger.info("Preenchendo nome do material '{}'.", nome_completo_material)
    page.locator("input[name='model-1']").fill(nome_completo_material)
    page.locator("button[name='lookup-model-1']").click()
    page.locator("button[name='submitSearch']").click()
    esperar_pagina_carregar(page)

    linhas = page.locator("table[name='paginationTable'] tbody tr").filter(
        has=page.locator("td").nth(2).filter(
            has_text=descricao_endereco
        )
    ).first

    logger.info("Verificando endereço '{}'.", descricao_endereco)
    if linhas.count() == 0:
        logger.info("O endereço '{}' não foi encontrado para este material.", descricao_endereco)
        return False
    
    page.locator("button[name='submitCancel']").click()
    esperar_pagina_carregar(page)

    logger.info("Endereço '{}' encontrado.", descricao_endereco)
    logger.info("Finalizou a verificação de existência de endereços para o material {}.", material["nome"])

    return True