from loguru import logger
from playwright.sync_api import Page

from flows.almoxarifado.gestao_de_estoque.classificacao_material.shared.escolher_tipo_flow import escolher_tipo
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def escolher_curva(page: Page, tipo: str) -> None:
    logger.info("Iniciou escolha de curva de material.")

    ctx = escopo(page)

    if ctx.locator("select[name='cdCurvaAbc']").is_visible():
        logger.info("Escolhendo tipo de curva de material '{}'.", tipo)
        escolher_tipo(page, "cdCurvaAbc", tipo)
    else:
        logger.info("Escolhendo tipo de curva de material '{}'.", tipo)
        escolher_tipo(page, "novaCurvaABC", tipo)

    ctx.locator("button[name='submitAdicionar']").click()
    aguardar_ajax_global(page)
    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou escolha de curva de material.")
