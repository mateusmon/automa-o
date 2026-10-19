from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def consultar_transferencia_entre_enderecos(page: Page, almoxarifado: dict, material: dict) -> None:
    logger.info("Iniciou consulta de transferência entre endereços no almoxarifado '{}'.", almoxarifado["nome"])

    nome_completo_material = f"{material['nome']} {material['complemento']}"
    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Preenchendo sigla do almoxarifado: '{}'.", almoxarifado["sigla"])
    preencher_campo(ctx, "input[name='model-1']", almoxarifado["sigla"])
    logger.info("Preenchendo nome do material: '{}'.", nome_completo_material)
    preencher_campo(ctx, "input[name='model-4']", nome_completo_material)
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de transferência entre endereços.")
