from loguru import logger
from playwright.sync_api import Page

from flows.patrimonio.movimentacao.baixa_bens.consultar_bem_baixa_flow import (
    consultar_bem_baixa,
)
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def preencher_itens(page: Page, ug: dict[str, str], bem: dict[str, str]) -> bool:
    logger.info("Iniciou preenchimento de itens.")

    ctx = escopo(page)

    ctx.locator("button[name='submitTabItens']").click()
    aguardar_ajax_global(page)
    ctx.locator("button[name='lookup-cdBemPerm-1-3']").click()
    aguardar_ajax_global(page)

    num_patrimonial = consultar_bem_baixa(page, ug, bem)

    if not num_patrimonial:
        logger.info("Nenhum bem encontrado para seleção.")
        return False

    aguardar_ajax_global(page)

    page.once("dialog", aceitar_confirmacao)
    ctx.locator("button[name='submitFinish']").click()

    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou preenchimento de itens.")
    return True


def aceitar_confirmacao(dialog):
    logger.info("Caixa de diálogo capturada: {}", dialog.message)
    dialog.accept()
    logger.info("Diálogo aceito.")
