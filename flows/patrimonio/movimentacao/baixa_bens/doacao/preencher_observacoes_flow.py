from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def preencher_observacoes(page: Page) -> None:
    logger.info("Iniciou o preenchimento de observações.")

    ctx = escopo(page)

    ctx.click("button[name='submitTabObservacoes']")
    aguardar_ajax_global(page)

    ctx.click("button[name='submitAddLine1']")
    aguardar_ajax_global(page)

    ctx.type("textarea[name='dsObs']", "🤔 hmm.", delay=50)

    ctx.click("button[name='submitBack']")
    aguardar_ajax_global(page)

    logger.info("Finalizou o preenchimento de observações.")
