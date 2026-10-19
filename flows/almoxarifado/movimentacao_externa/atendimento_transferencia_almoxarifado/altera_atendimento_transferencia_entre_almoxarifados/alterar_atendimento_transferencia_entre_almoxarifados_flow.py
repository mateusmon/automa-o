from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, clicar_com_ajax, esperar_sucesso_ou_erro


def alterar_atendimento_transferencia_entre_almoxarifados(page: Page) -> bool:
    logger.info("Iniciou alteração de atendimento da transferência entre almoxarifados.")

    ctx = escopo(page)

    linha = ctx.locator("table tbody[name='MovimentosTitles'] tr").first
    coluna = linha.locator("td").count()
    coluna_quantidade = coluna - 2

    campo_qf = ctx.locator(f"input[name='qtAtendido-1-1-{coluna_quantidade}']")
    quantidade = campo_qf.input_value()

    if quantidade == "1":
        nova_quantidade = "0"
    else:
        nova_quantidade = "1"

    botao_locator = ctx.locator(f"button[name='edit-qtPedidoPendente-1-1-{coluna}']")
    clicar_com_ajax(ctx, botao_locator)
    aguardar_ajax_global(page)
    campo_lote = ctx.locator("input[name='qtAtendidoLote-1-6']")

    if campo_lote.is_visible() and campo_lote.is_enabled():
        logger.info("Alterando quantidade de lote: '{}' -> '{}'.", campo_lote.input_value(), nova_quantidade)
        campo_lote.fill(nova_quantidade)

    clicar_com_ajax(ctx, ctx.locator("button[name='submitBack']"))

    if campo_qf.is_disabled():
        logger.warning("O campo 'Q.F.' está desabilitada.")
        return False

    logger.info("Alterando quantidade de atendimento: '{}' -> '{}'.", campo_qf.input_value(), nova_quantidade)
    campo_qf.fill(nova_quantidade)
    clicar_com_ajax(ctx, ctx.locator("button[name='submitFinish']"))
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou alteração de atendimento da transferência entre almoxarifados.")
    return True
