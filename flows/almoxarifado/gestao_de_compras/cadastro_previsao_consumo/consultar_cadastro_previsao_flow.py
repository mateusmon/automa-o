from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_cadastro(page: Page, ur_data: dict[str, str], material: dict[str, str]) -> None:
    logger.info("Iniciou consulta de Cadastro de Previsão de Consumo da UR {}.", ur_data["nome"])

    ctx = escopo(page)
    
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Preenchendo UR '{}'.", ur_data["nome"])
    ctx.locator("input[name='model-1']").type(ur_data["nome"])
    ctx.locator("button[name='lookup-model-1']").click()
    aguardar_ajax_global(page)

    logger.info("Preenchendo material '{}'.", material["nome"])
    ctx.locator("input[name='model-12']").type(f"{material["nome"]} {material["complemento"]}")
    ctx.locator("button[name='lookup-model-12']").click()
    aguardar_ajax_global(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de Cadastro de Previsão de Consumo da UR {}.", ur_data["nome"])
