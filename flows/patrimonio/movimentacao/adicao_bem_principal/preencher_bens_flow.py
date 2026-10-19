from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import preencher_autocomplete, aguardar_ajax_global, esperar_sucesso_ou_erro


def preencher_bens(page: Page, num_patrim: str) -> None:
    logger.info("Iniciou preenchimento de bens {}.", num_patrim)

    ctx = escopo(page)

    preencher_autocomplete(ctx, "input[name='cdBemPerm-1-3']", num_patrim)
    
    ctx.locator("button[name='submitConfirm']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou preenchimento de bens {}.", num_patrim)
