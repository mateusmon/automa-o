from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo


def finalizar_inventario(page: Page, material: dict) -> None:
    logger.info("Finalizando inventário do material '{}'.".format(material['nome']))

    nome_completo_material = f"{material['nome']} {material['complemento']}"
    ctx = escopo(page)

    logger.info("Preenchendo nome do material '{}'.", nome_completo_material)
    preencher_campo(ctx, "input[name='cdBemServico-1-2']", nome_completo_material, lookup_name="lookup-cdBemPerm-1-2")

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Inventário do material '{}' finalizado.", material['nome'])
