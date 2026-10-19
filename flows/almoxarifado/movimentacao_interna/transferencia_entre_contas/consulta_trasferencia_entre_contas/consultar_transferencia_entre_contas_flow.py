from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def consultar_transferencia_entre_contas(page: Page, material: dict[str, str]) -> None:
    logger.info("Iniciou consulta de transferência entre contas para o material '{}'.", material['nome'])

    ctx = escopo(page)
    nome_completo_material = f"{material['nome']} {material['complemento']}"

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Preenchendo nome do material: '{}'.", nome_completo_material)
    preencher_campo(ctx, "input[name='model-3']", nome_completo_material)
    aguardar_ajax_global(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de transferência entre contas para o material '{}'.", material['nome'])