from loguru import logger
from playwright.sync_api import Frame, Page

from utils.versao import escopo


def verificar_existencia_siaf(page: Page, tipo_bem: str | None = None) -> bool:
    logger.info("Iniciou verificação da existência de integração SIAF.")

    ctx = escopo(page)
    existe = _existe(ctx, tipo_bem)

    logger.info("Resultado da verificação de integração SIAF: {existe}", existe=existe)
    logger.info("Finalizou verificação da existência de integração SIAF.")
    return existe


def _existe(ctx: Page | Frame, tipo_bem: str | None) -> bool:
    botao_siaf = ctx.locator("button[title='Integração com SIAF']").first
    return botao_siaf.is_visible()
