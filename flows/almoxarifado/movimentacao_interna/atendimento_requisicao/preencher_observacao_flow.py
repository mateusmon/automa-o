from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import clicar_com_ajax


def preencher_observacao(page: Page) -> None:
    logger.info("Iniciou preenchimento da aba de observação.")

    ctx = escopo(page)

    clicar_com_ajax(ctx, "button[name='submitTabObservacoes']")
    clicar_com_ajax(ctx, "button[name='submitAddLine']")

    logger.info(
        "Preenchendo observação: 'Observacao de recebimento de requisição Automatizado'."
    )
    ctx.locator("textarea[name='dsObs']").fill(
        "Observacao de recebimento de requisição Automatizado"
    )

    try:
        clicar_com_ajax(ctx, "button[name='submitBack']")
    except Exception:
        logger.info("Não foi possível preencher observação.")
        clicar_com_ajax(ctx, "button[name='submitCancel']")

    clicar_com_ajax(ctx, "button[name='submitFinish']")

    logger.info("Finalizou preenchimento da aba de observação.")
