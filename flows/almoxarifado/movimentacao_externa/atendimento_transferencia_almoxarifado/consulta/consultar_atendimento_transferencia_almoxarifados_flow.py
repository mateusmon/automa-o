from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def consultar_atendimento(
        page: Page, 
        almoxarifado: dict[str, str], 
        almoxarifado_solicitante: dict[str, str], 
        material: dict[str, str]
) -> None:
    logger.info("Iniciou consulta de atendimento de transferência entre almoxarifados: {} -> {}.", almoxarifado["nome"], almoxarifado_solicitante["nome"])

    nome_completo_material = f"{material['nome']} {material['complemento']}"
    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    # Preencher almoxarifado atendimento
    logger.info("Preenchendo sigla do almoxarifado de atendimento: '{}'.", almoxarifado["sigla"])
    preencher_campo(ctx, "input[name='model-0']", almoxarifado["sigla"])

    # Preencher almoxarifado solicitante
    logger.info("Preenchendo sigla do almoxarifado solicitante: '{}'.", almoxarifado_solicitante["sigla"])
    preencher_campo(ctx, "input[name='model-1']", almoxarifado_solicitante["sigla"])

    # Preencher material
    logger.info("Preenchendo nome do material: '{}'.", nome_completo_material)
    preencher_campo(ctx, "input[name='model-8']", nome_completo_material)

    # Situação = Atendida
    logger.info("Preenchendo situação da transferência: 'ATENDIDA'.")
    preencher_campo(ctx, "input[name='model-10']", "ATENDIDA")

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de atendimento de transferência entre almoxarifados: {} -> {}.", almoxarifado["nome"], almoxarifado_solicitante["nome"])
