from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, select_tipo


def escolher_criticidade(page: Page, tipo: str) -> None:
    logger.info("Iniciou escolha de criticidade de material.")

    ctx = escopo(page)

    logger.info("Escolhendo tipo de criticidade de material '{}'.", tipo)
    select_tipo(ctx, "cdNivelCritico", tipo)

    ctx.locator("button[name='submitAdicionar']").click()
    aguardar_ajax_global(page)
    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou escolha de criticidade de material '{}'.", tipo)
