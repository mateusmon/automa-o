from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def preencher_observacao(page: Page) -> None:
    logger.info("Iniciou preenchimento da aba de observação.")

    ctx = escopo(page)

    ctx.get_by_role("button", name="Observações").click()
    aguardar_ajax_global(page)

    ctx.get_by_title("Adicionar observações").click()
    aguardar_ajax_global(page)

    logger.info("Preenchendo observação: 'Observacao de atendimento de requisição Automatizado'.")
    ctx.locator("textarea[name='dsObs']").fill("Observacao de atendimento de requisição Automatizado")

    ctx.get_by_role("button", name="Retornar").click()
    aguardar_ajax_global(page)

    ctx.get_by_role("button", name="Atendimento").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou preenchimento da aba de observação.")
