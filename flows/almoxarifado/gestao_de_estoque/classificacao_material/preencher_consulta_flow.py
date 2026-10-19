from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def preencher_consulta(page: Page, almoxarifado: dict[str, str], material: dict[str, str]) -> None:
    logger.info("Iniciou preenchimento de consulta na página de classificação do material.")

    nome_completo_material = f"{material['nome']} {material['complemento']}"
    ctx = escopo(page)

    logger.info("Preenchendo sigla do almoxarifado '{}'.", almoxarifado["sigla"])
    preencher_campo(ctx, "input[name='listAlmoxs']", almoxarifado["sigla"])
    logger.info("Preenchendo nome do material '{}'.", nome_completo_material)
    preencher_campo(ctx, "input[name='bemServico']", nome_completo_material)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou preenchimento de consulta na página de classificação do material.")
