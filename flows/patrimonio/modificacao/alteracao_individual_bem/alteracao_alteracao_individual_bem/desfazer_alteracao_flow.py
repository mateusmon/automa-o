from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo


def desfazer_alteracao(page: Page, fornecedor_padrao: dict[str, str]) -> None:
    logger.info("Iniciou desfazer alteração.")

    ctx = escopo(page)
    preencher_campo(ctx, "input[name='agente']", fornecedor_padrao["nome"])

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou desfazer alteração.")
