from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, clicar_com_ajax, esperar_sucesso_ou_erro


def alterar_quantidade(page: Page) -> None:
    logger.info("Iniciou alteração de quantidade fornecida.")

    ctx = escopo(page)

    tabela = ctx.locator("table.tabela.nested").last
    td_count = tabela.locator("tbody tr").first.locator("td").count()

    quantidade_atendida = ctx.locator("input[name^='qtAtendido-1-1']").input_value()
    
    clicar_com_ajax(ctx, f"button[name='edit-qtPedidoPendente-1-1-{td_count}']")
    aguardar_ajax_global(page)


    if quantidade_atendida == "0":
        nova_quantidade = "1"
    else:
        nova_quantidade = "0"

    if ctx.locator("input[name='qtAtendidoLote-1-6']").is_visible():
        logger.info("Alterando quantidade de lote: '{}' -> '{}'.", ctx.locator("input[name='qtAtendidoLote-1-6']").input_value(), nova_quantidade)
        ctx.locator("input[name='qtAtendidoLote-1-6']").fill(nova_quantidade)

    ctx.locator("button[name='submitBack']").click()
    aguardar_ajax_global(page)

    logger.info("Alterando quantidade atendida: '{}' -> '{}'.", quantidade_atendida, nova_quantidade)
    ctx.locator("input[name^='qtAtendido-1-1']").dblclick()
    ctx.locator("input[name^='qtAtendido-1-1']").fill(nova_quantidade)

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou alteração de quantidade fornecida.")
