from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_entradas(page: Page, ug: dict[str, str], material: dict[str, str]) -> None:
    nome_material = material["nome"]
    complemento_material = material["complemento"]
    nome_completo_material = f"{nome_material} {complemento_material}"

    logger.info("Iniciou consulta de entradas para o material '{}'.", nome_completo_material)
    
    ctx = escopo(page)

    ctx.get_by_role("button", name="Consulta", exact=True).click()
    aguardar_ajax_global(page)

    ctx.locator("input[name='model-2']").type(ug["codigo"], delay=50)
    ctx.locator("button[name='lookup-model-2']").click()
    aguardar_ajax_global(page)

    ctx.locator("input[name='model-6']").type(nome_completo_material, delay=50)
    ctx.locator("button[name='lookup-model-6']").click()
    aguardar_ajax_global(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de entradas para o material '{}'.", nome_completo_material)
