from  loguru import logger
from playwright.sync_api import Page

from utils.waits import esperar_pagina_carregar

def consultar_enderecamento_material(page: Page, almoxarifado: dict[str, str], material: dict[str, str]) -> None:
    logger.info("Consultando endereçamento de material.")

    nome_completo_material = f"{material["nome"]} {material["complemento"]}"

    page.locator("button[name='submitSearch']").click()
    esperar_pagina_carregar(page)

    # Preenche Almoxarifado
    logger.info("Consultando almoxarifado '{}'.", almoxarifado["sigla"])
    page.locator("input[name='model-0']").fill(almoxarifado["sigla"])
    page.locator("button[name='lookup-model-0']").click()

    # Preenche Material
    logger.info("Consultando material '{}'.", nome_completo_material)
    page.locator("input[name='model-1']").fill(nome_completo_material)
    page.locator("button[name='lookup-model-1']").click()

    page.locator("button[name='submitSearch']").click()
    esperar_pagina_carregar(page)

    logger.info("Endereçamento de material consultado.")