from loguru import logger
from playwright.async_api import Page

from utils.versao import escopo
from utils.waits import select_tipo


def escolher_modalidade(page: Page, modalidade: str) -> None:
    logger.info("Iniciou escolha da modalidade.")

    ctx = escopo(page)

    ctx.locator("select[name='tipoMovimento']").wait_for(state="visible")

    select_tipo(ctx, "tipoMovimento", modalidade)

    logger.info("Finalizou escolha da modalidade.")