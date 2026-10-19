from loguru import logger
from playwright.sync_api import Page

from flows.patrimonio.shared.consultar_bem_flow import consultar_bem
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, clicar_com_ajax


def preencher_itens_transferencia_externa(page: Page, ug: dict[str, str], bem: dict[str, str]) -> bool:
    logger.info("Iniciou o preenchimento de itens da Transferência Externa na UG '{}'.", ug["nome"])

    ctx = escopo(page)

    clicar_com_ajax(ctx, ctx.locator("button[name='submitTabItens']"))

    botao_excluir = ctx.locator("button[name='submitPurgeLines1']")
    botao_excluir.wait_for(state="visible")
    clicar_com_ajax(ctx, botao_excluir)
    clicar_com_ajax(ctx, ctx.locator("button[name='submitAddLine1']"))
    clicar_com_ajax(ctx, ctx.locator("button[name='lookup-cdBemPerm-1-3']"))

    if not consultar_bem(page, ug, bem):
        logger.info("Bem '{}' não encontrado na UG '{}'.", bem["nome"], ug["nome"])
        return False

    aguardar_ajax_global(page)

    logger.info("Bem '{}' encontrado na UG '{}'.", bem["nome"], ug["nome"])
    logger.info("Finalizou o preenchimento de itens da Transferência Externa na UG '{}'.", ug["nome"])
    return True