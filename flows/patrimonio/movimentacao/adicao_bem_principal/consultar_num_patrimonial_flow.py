from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global

def consultar_num_patrimonial(page: Page, ul: dict[str, str], bem: dict[str, str]) -> None:
    logger.info("Iniciou consulta do Número Patrimonial {}.", bem["nome"])

    ctx = escopo(page)

    linha = ctx.locator("table.tabelaComRolagem tbody tr").filter(
        has=ctx.locator("td").nth(2).locator("input:not([disabled])")
    ).first

    linha.locator("button[name^='lookup-cdBemPerm']").click()
    aguardar_ajax_global(page)

    ctx.locator("input[name='model-5']").type(ul["sigla"], delay=50)
    ctx.locator("button[name='lookup-model-5']").click()
    aguardar_ajax_global(page)

    ctx.locator("input[name='model-15']").type(f"{bem['nome']} {bem['complemento']}", delay=50)
    ctx.locator("button[name='lookup-model-15']").click()
    aguardar_ajax_global(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    if ctx.locator("button[name='submitBack']").is_visible():
        ctx.locator("button[name='submitBack']").click()
        aguardar_ajax_global(page)

    logger.info("Finalizou consulta do Número Patrimonial {}.", bem["nome"])