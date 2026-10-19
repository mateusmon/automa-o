from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo

def alterar_destino(page: Page, destino: dict[str, str], destino_padrao: dict[str, str]) -> None:
    logger.info("Alterando destino da Transferência Externa de Destino: '{}', e Destino Padrão: '{}'.", destino["nome"], destino_padrao["nome"])

    ctx = escopo(page)

    if destino_padrao["nome"] in ctx.locator("input[name='fornecedor']").input_value():
        preencher_campo(ctx, "input[name='fornecedor']", destino["nome"])
    else:
        preencher_campo(ctx, "input[name='fornecedor']", destino_padrao["nome"])

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Destino alterado. Destino: '{}', e Destino Padrão: '{}'.", destino["nome"], destino_padrao["nome"])