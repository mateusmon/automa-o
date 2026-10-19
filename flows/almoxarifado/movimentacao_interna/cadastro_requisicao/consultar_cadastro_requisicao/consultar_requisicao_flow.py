from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def consultar_requisicao(page: Page, almoxarifado: dict, ur: dict, material: dict) -> None:
    logger.info("Iniciou consulta de requisição no almoxarifado '{}'.", almoxarifado["nome"])

    ctx = escopo(page)
    _consultar(ctx, page, almoxarifado, ur, material)

    logger.info("Finalizou consulta de requisição no almoxarifado '{}'.", almoxarifado["nome"])


def _consultar(ctx, page: Page, almoxarifado: dict, ur: dict, material: dict) -> None:
    nome_completo_material = f"{material['nome']} {material['complemento']}"

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Preenchendo sigla do almoxarifado: '{}'.", almoxarifado["sigla"])
    preencher_campo(ctx, "input[name='model-2']", almoxarifado["sigla"])

    logger.info("Preenchendo UR: '{}'.", ur["nome"])
    preencher_campo(ctx, "input[name='model-6']", ur["nome"])
    preencher_campo(ctx, "input[name='model-15']", nome_completo_material)
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)
