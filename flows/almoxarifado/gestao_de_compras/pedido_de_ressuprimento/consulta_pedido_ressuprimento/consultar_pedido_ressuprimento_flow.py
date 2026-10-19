from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def consultar_pedido_ressuprimento(page: Page, almoxarifado: dict, material: dict) -> bool:
    logger.info("Iniciou consulta de pedido de ressuprimento.")

    ctx = escopo(page)
    resultado = _consultar(ctx, page, almoxarifado, material)

    logger.info("Finalizou consulta de pedido de ressuprimento.")
    return resultado


def _consultar(ctx, page: Page, almoxarifado: dict, material: dict) -> bool:
    nome_completo_material = f"{material['nome']} {material['complemento']}"

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Preenchendo sigla do almoxarifado '{}'.", almoxarifado["sigla"])
    preencher_campo(ctx, "input[name='model-1']", almoxarifado["sigla"])
    aguardar_ajax_global(page)

    logger.info("Preenchendo material '{}'.", nome_completo_material)
    preencher_campo(ctx, "input[name='model-4']", nome_completo_material)
    aguardar_ajax_global(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    linha = ctx.locator("table[name='paginationTable'] tbody tr").filter(
        has=ctx.locator("td").nth(0).filter(has_text=almoxarifado["nome"])
    ).first

    linha.wait_for(state="visible")

    if linha.count() == 0:
        logger.info("Nenhum pedido encontrado para almoxarifado '{}'.", almoxarifado["sigla"])
        return False

    linha.locator("button[name='submitUse']").click()
    aguardar_ajax_global(page)

    return True