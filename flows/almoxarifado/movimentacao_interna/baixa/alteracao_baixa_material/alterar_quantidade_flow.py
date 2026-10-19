from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def alterar_quantidade(page: Page) -> None:
    logger.info("Iniciou alteração de quantidade de baixa de material.")

    ctx = escopo(page)

    quantidade = ctx.locator("input[name^='qtBaixa-1']").input_value()

    if quantidade == "1":
        nova_quantidade = "2"
    else:
        nova_quantidade = "1"

    if ctx.locator("button[name='edit-itens-1-7']").is_visible():
        ctx.locator("button[name='edit-itens-1-7']").click()
        aguardar_ajax_global(page)

        if ctx.locator("input[name='qtLote-1-6']").is_visible():
            logger.info("Alterando quantidade de lote: '{}' -> '{}'.", ctx.locator("input[name='qtLote-1-6']").input_value(), nova_quantidade)
            ctx.locator("input[name='qtLote-1-6']").fill(nova_quantidade)

        ctx.locator("button[name='submitBack']").click()
        aguardar_ajax_global(page)

    logger.info("Alterando quantidade de baixa de material: '{}' -> '{}'.", quantidade, nova_quantidade)
    ctx.locator("input[name^='qtBaixa-1']").dblclick()
    ctx.locator("input[name^='qtBaixa-1']").fill(nova_quantidade)

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou alteração de quantidade de baixa de material.")
