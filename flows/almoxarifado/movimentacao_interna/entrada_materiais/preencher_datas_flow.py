from datetime import date
from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo


def preencher_datas(page: Page) -> None:
    """
    Preenche as datas de recebimento e de contabilização (atesto) dos dados
    gerais da entrada com a data de hoje. O campo de atesto só é preenchido
    quando está habilitado.

    Parâmetros:
        page (Page): Instância da página do Playwright.
    """
    logger.info("Iniciou preenchimento das datas.")

    ctx = escopo(page)
    data_hoje = date.today().strftime("%d%m%Y")

    data_recebimento = ctx.locator('input[name="dtRecebimento"]')
    logger.info("Preenchendo data de recebimento: '{}'.", data_hoje)
    data_recebimento.clear()
    data_recebimento.type(data_hoje, delay=50)

    data_atesto = ctx.locator('input[name="dtContabil"]')
    if data_atesto.is_enabled():
        logger.info("Preenchendo data de atesto: '{}'.", data_hoje)
        data_atesto.clear()
        data_atesto.type(data_hoje, delay=50)

    logger.info("Finalizou preenchimento das datas.")
