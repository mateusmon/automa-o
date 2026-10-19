from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import preencher_campo


def preencher_dados_gerais(
    page: Page, ug: dict[str, str], almoxarifado: dict[str, str]
) -> None:
    logger.info(
        "Iniciou preenchimento de dados gerais no almoxarifado '{}'.",
        almoxarifado["nome"],
    )

    ctx = escopo(page)

    # Preencher U.G.
    if not page.locator("select[name='listaUg']"):
        logger.info("Preenchendo código da UG: '{}'.", ug["codigo"])
        preencher_campo(ctx, "input[name='cdUg']", ug["codigo"])

    # Preencher Almoxarifado
    logger.info("Preenchendo sigla do almoxarifado: '{}'.", almoxarifado["sigla"])
    preencher_campo(ctx, "input[name='cdAlmox']", almoxarifado["sigla"])

    logger.info(
        "Finalizou preenchimento de dados gerais no almoxarifado '{}'.",
        almoxarifado["nome"],
    )
