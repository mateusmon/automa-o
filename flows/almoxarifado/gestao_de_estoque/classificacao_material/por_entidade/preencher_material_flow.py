from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def preencher_material(page: Page, material: dict) -> None:
    nome_completo_material = f"{material['nome']} {material['complemento']}"

    logger.info("Iniciou preenchimento de material '{}'.", nome_completo_material)

    ctx = escopo(page)

    logger.info("Preenchendo nome do material '{}'.", nome_completo_material)
    preencher_campo(ctx, "input[name='bemServico']", nome_completo_material)
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou preenchimento de material '{}'.", nome_completo_material)
