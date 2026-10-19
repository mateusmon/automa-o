from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_requisicao(page: Page, ug: dict[str, str], bem: dict[str, str]) -> None:
    logger.info("Iniciou consulta de requisição. UG: '{}'.", ug["codigo"])

    ctx = escopo(page)

    ctx.get_by_role("button", name="Consulta", exact=True).click()
    aguardar_ajax_global(page)

    ctx.locator("input[name='model-1']").type(ug["codigo"], delay=50)
    ctx.locator("button[name='lookup-model-1']").click()
    aguardar_ajax_global(page)

    ctx.locator("input[name='model-8']").type(f"{bem['nome']} {bem['complemento']}", delay=50)
    ctx.locator("button[name='lookup-model-8']").click()
    aguardar_ajax_global(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de requisição. UG: '{}'.", ug["codigo"])
