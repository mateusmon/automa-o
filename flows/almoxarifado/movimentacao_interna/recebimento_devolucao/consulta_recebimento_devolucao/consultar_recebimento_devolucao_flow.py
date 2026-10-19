from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def consultar_recebimento_devolucao(page: Page, almoxarifado: dict, ug: dict) -> None:
    logger.info(
        "Iniciou consulta recebimento de devolução de materiais no almoxarifado: {}.",
        almoxarifado["nome"],
    )

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    # Ele vai selecionar a UG que tenha exatamente o mesmo nome.
    logger.info("Preenchendo nome da UG: '{}'.", ug["nome"])
    preencher_campo(ctx, "input[name='model-1']", ug["codigo"], igual=True)
    logger.info("Preenchendo nome do almoxarifado: '{}'.", almoxarifado["nome"])
    preencher_campo(ctx, "input[name='model-2']", almoxarifado["nome"])

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info(
        "Finalizou consulta recebimento de devolução de materiais no almoxarifado: {}.",
        almoxarifado["nome"],
    )
