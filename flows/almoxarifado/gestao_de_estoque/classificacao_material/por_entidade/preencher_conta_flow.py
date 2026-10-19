from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def preencher_conta(page: Page, material: dict[str, str], almoxarifado: dict[str, str]) -> None:
    logger.info("Iniciou preenchimento de conta para o material '{}' no almoxarifado '{}'.", material["nome"], almoxarifado["sigla"])

    ctx = escopo(page)

    ctx.locator("button[name='lookup-bemServico']").click()
    aguardar_ajax_global(page)

    logger.info("Preenchendo sigla do almoxarifado '{}'.", almoxarifado["sigla"])
    preencher_campo(ctx, "input[name='model-1']", almoxarifado["sigla"])
    logger.info("Preenchendo nome do material '{}'.", material["nome"])
    ctx.locator("input[name='model-4']").fill(f"{material['nome']}")

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    # Esperando até a primeira linha da tabela ficar visível
    ctx.locator("tr[name='searchResultData']").first.wait_for(state="visible")
    # Extraindo o número da conta contábil da primeira linha
    conta = ctx.locator("td[name='cell-1-3']").inner_text().split(" - ", 1)[0]

    ctx.locator("button[name='submitCancel']").last.click()
    aguardar_ajax_global(page)

    logger.info("Preenchendo conta contábil '{}' para o material '{}'.", conta, material["nome"])
    preencher_campo(ctx, "input[name='bemServico']", material["nome"])
    preencher_campo(ctx, "input[name='conta']", conta, igual=True)
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou preenchimento de conta para o material '{}' no almoxarifado '{}'.", material["nome"], almoxarifado["sigla"])
