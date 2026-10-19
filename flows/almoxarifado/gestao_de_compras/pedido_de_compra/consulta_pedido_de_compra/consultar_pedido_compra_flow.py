from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo

def consultar_pedido_compra(page: Page, ua: dict, material: dict):
    logger.info("Consultando pedido de compra.")

    nome_completo_material = f"{material["nome"]} {material["complemento"]}"

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()

    aguardar_ajax_global(page)

    # Preencher UA
    logger.info("Preenchendo UA '{}'.", ua["nome"])
    preencher_campo(ctx, "input[name='model-1']", ua["nome"])

    # Preencher Material
    logger.info("Preenchendo material '{}'.", nome_completo_material)
    preencher_campo(ctx, "input[name='model-2']", nome_completo_material)

    ctx.locator("button[name='submitSearch']").click()

    aguardar_ajax_global(page)

    total = ctx.locator("span[name='searchResultSize']")
    total.wait_for(state="visible")

    linha = ctx.locator("table[name='paginationTable'] tbody tr").filter(
        has=ctx.locator("td").nth(1).filter(
            has_text=ua["nome"]
        )
    ).first

    if total.inner_text().strip() == "0" or linha.count() == 0:
        logger.info("Nenhum pedido encontrado para UA '{}'.", ua["nome"])
        return False
    
    linha.locator("button[name='submitUse']").click()

    aguardar_ajax_global(page)

    logger.info("Pedido de compra consultado.")
    
    return True