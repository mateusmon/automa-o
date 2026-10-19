from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_conta_contabil(page: Page, bem: dict[str, str]) -> None:
    logger.info("Iniciou consulta de modificação de conta contábil.")

    ctx = escopo(page)
    nome_completo_bem = f"{bem['nome']} {bem['complemento']}"

    ctx.locator("button[name='submitSearch']").wait_for(state="visible")

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    ctx.locator("input[name='model-2']").fill(nome_completo_bem)
    ctx.locator("button[name='lookup-model-2']").click()
    aguardar_ajax_global(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    ctx.get_by_role("button", name="Cancelar").wait_for(state="visible")

    logger.info("Finalizou consulta de modificação de conta contábil.")
