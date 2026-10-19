from playwright.sync_api import Page, expect
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def consultar_ultima_entrada(page: Page, almoxarifado: dict[str, str], material: dict[str, str]) -> bool:
    logger.info("Iniciou consulta da última entrada no almoxarifado '{}' para o material '{}'.", almoxarifado["sigla"], material["nome"])

    ctx = escopo(page)

    ctx.get_by_role("button", name="Consulta", exact=True).click()
    aguardar_ajax_global(page)

    logger.info("Preenchendo sigla do almoxarifado: '{}'.", almoxarifado["sigla"])
    preencher_campo(ctx, 'input[name="model-2"]', almoxarifado["sigla"])
    logger.info("Preenchendo nome do material: '{}'.", material["nome"])
    preencher_campo(ctx, 'input[name="model-13"]', material["nome"])

    ctx.get_by_title("Consultar novo registro").click()
    aguardar_ajax_global(page)

    ctx.locator("table[name='paginationTable'] tbody").wait_for(state="visible")

    logger.info("Finalizou consulta da última entrada.")

    if not ctx.locator('td[name="cell-1-1"]').is_visible():
        logger.info("Não há registro de entradas.")
        return False

    ctx.locator('td[name="tdMultiple-1-6"]').locator('button[name="submitUse"]').click()
    aguardar_ajax_global(page)

    expect(ctx.get_by_role("button", name="Origem")).to_be_visible()

    return True
