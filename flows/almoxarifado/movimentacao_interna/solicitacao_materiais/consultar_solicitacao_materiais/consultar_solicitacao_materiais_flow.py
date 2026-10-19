from datetime import datetime

from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_almoxarifado
from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_solicitacao_materiais(page: Page, almoxarifado: dict, ur: dict, material: dict) -> None:
    logger.info("Iniciou consulta de solicitação de materiais no almoxarifado '{}' para o material '{}'.", almoxarifado["nome"], material["nome"])

    ctx = escopo(page)
    _consultar(ctx, page, almoxarifado, ur, material)

    logger.info("Finalizou consulta de solicitação de materiais no almoxarifado '{}' para o material '{}'.", almoxarifado["nome"], material["nome"])


def _consultar(ctx, page: Page, almoxarifado: dict, ur: dict, material: dict) -> None:
    nome_completo_material = f"{material['nome']} {material['complemento']}"

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Preenchendo nome do almoxarifado: '{}'.", almoxarifado["nome"])
    ctx.locator("input[name='model-1']").fill(almoxarifado["nome"])
    ctx.locator("button[name='lookup-model-1']").click()
    aguardar_ajax_global(page)

    logger.info("Preenchendo nome da UR: '{}'.", ur["nome"])
    ctx.locator("input[name='model-2']").fill(ur["nome"])
    ctx.locator("button[name='lookup-model-2']").click()
    aguardar_ajax_global(page)

    data_final_str = obter_data_almoxarifado(page, formato="DD/MM/YYYY")
    data_dt = datetime.strptime(data_final_str, "%d/%m/%Y")

    data_inicial_str = data_dt.replace(day=1).strftime("%d/%m/%Y")

    logger.info("Preenchendo período de consulta: '{}' até '{}'.", data_inicial_str, data_final_str)

    input_de = ctx.locator("input[name='model-5-from']")
    input_de.click()
    input_de.fill(data_inicial_str)
    input_de.dispatch_event("change")

    input_ate = ctx.locator("input[name='model-5-to']")
    input_ate.click()
    input_ate.clear()
    input_ate.fill(data_final_str)
    input_ate.dispatch_event("change")

    logger.info("Preenchendo nome do material: '{}'.", nome_completo_material)
    input_material = ctx.locator("input[name='model-8']")
    input_material.click()
    input_material.fill(nome_completo_material)
    
    ctx.locator("button[name='lookup-model-8']").click()
    aguardar_ajax_global(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)
