from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, selecionar_resultado, preencher_campo


def consultar_cadastro_transferencia_completa(page: Page, almoxarifado: dict[str, str], almoxarifado_solicitante: dict[str, str], material: dict[str, str]) -> None:
    logger.info("Iniciou consulta de cadastro de transferência entre almoxarifados: {} -> {}.", almoxarifado["nome"], almoxarifado_solicitante["nome"])

    ctx = escopo(page)
    nome_completo_material = f"{material['nome']} {material['complemento']}"

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    # Preencher almoxarifado de atendimento
    logger.info("Preenchendo sigla do almoxarifado de atendimento: '{}'.", almoxarifado["sigla"])
    preencher_campo(ctx, "input[name='model-0']", almoxarifado["sigla"])

    if ctx.get_by_text("Almoxarifado - Resultado da").is_visible():
        selecionar_resultado(ctx, "table[name='paginationTable'] tbody tr", 3, almoxarifado["sigla"])

    # Preencher almoxarifado solicitante
    logger.info("Preenchendo sigla do almoxarifado solicitante: '{}'.", almoxarifado_solicitante["sigla"])
    preencher_campo(ctx, "input[name='model-1']", almoxarifado_solicitante["sigla"])
    
    # Preencher material
    logger.info("Preenchendo nome do material: '{}'.", nome_completo_material)
    preencher_campo(ctx, "input[name='model-8']", nome_completo_material)

    # Preencher situação PRONTA PARA ATENDER
    logger.info("Preenchendo situação da transferência: 'ATENDER'.")
    preencher_campo(ctx, "input[name='model-10']", "ATENDER")
    
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)
    ctx.locator("button[name='submitUse']").first.click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de cadastro de transferência entre almoxarifados: {} -> {}.", almoxarifado["nome"], almoxarifado_solicitante["nome"])