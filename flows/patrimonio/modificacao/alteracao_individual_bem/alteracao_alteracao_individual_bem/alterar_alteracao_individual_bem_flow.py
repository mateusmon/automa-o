from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo


def alterar_alteracao_individual_bem(page: Page, fornecedor_alteracao: dict[str, str], fornecedor_padrao: dict[str, str]) -> None:
    logger.info("Iniciou alteração de alteração individual do bem.")

    ctx = escopo(page)

    if fornecedor_padrao["nome"] in ctx.locator("input[name='agente']").input_value():
        preencher_campo(ctx, "input[name='agente']", fornecedor_alteracao["nome"])
    else:
        preencher_campo(ctx, "input[name='agente']", fornecedor_padrao["nome"])

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou alteração de alteração individual do bem.")