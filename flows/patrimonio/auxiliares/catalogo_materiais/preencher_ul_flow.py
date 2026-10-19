from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo


def preencher_ul(page: Page, ul: dict[str, str]) -> None:
    logger.info(
        "Iniciou preenchimento da UL '{}' do Catálogo de Materiais.", ul["sigla"]
    )

    ctx = escopo(page)

    ctx.locator("button[name='submitTabUl']").click()
    aguardar_ajax_global(page)

    logger.info("Preenchendo sigla da UL: '{}'.", ul["sigla"])
    preencher_campo(ctx, "input[name='cdUl-1-2']", ul["sigla"])

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info(
        "Finalizou preenchimento da UL '{}' do Catálogo de Materiais.", ul["sigla"]
    )
