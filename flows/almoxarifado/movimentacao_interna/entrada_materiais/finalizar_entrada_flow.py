from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, clicar_com_ajax, esperar_sucesso_ou_erro


def finalizar_entrada(page: Page) -> None:
    logger.info("Finalizando entrada.")

    ctx = escopo(page)

    clicar_com_ajax(ctx, 'button[name="submitFinish"]')
    aguardar_ajax_global(page)

    if ctx.get_by_role("heading", name="Materiais com quantidade em").is_visible():
        ctx.locator("input[name='confirmarEntradaComEstoqueCkb']").check()
        aguardar_ajax_global(page)
        logger.info("Preenchendo justificativa: 'UMA BOA JUSTIFICATIVA.'")
        ctx.locator("textarea[name='txJustificativaSaldoEstoque']").fill("UMA BOA JUSTIFICATIVA.")
        clicar_com_ajax(ctx, 'button[name="submitFinish"]')

    esperar_sucesso_ou_erro(ctx)

    logger.info("Entrada finalizada com sucesso.")
