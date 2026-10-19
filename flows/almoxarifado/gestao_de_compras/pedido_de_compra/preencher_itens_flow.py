from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo


def preencher_itens(page: Page, material: dict[str, str]) -> None:
    logger.info("Iniciou preenchimento de itens do pedido de compra.")

    ctx = escopo(page)
    _preencher(ctx, page, material)

    logger.info("Finalizou preenchimento de itens do pedido de compra.")


def _preencher(ctx, page: Page, material: dict[str, str]) -> None:
    nome_completo = f"{material['nome']} {material['complemento']}"

    ctx.get_by_role("button", name="Itens").click()
    aguardar_ajax_global(page)

    linha = ctx.locator("table tbody[name='tboItens'] tr").first

    linha.wait_for(state="visible")

    logger.info("Preenchendo material '{}'.", nome_completo)
    preencher_campo(ctx, "input[name='cdBemServico-1-3']", nome_completo)

    ctx.locator("input[name='qtPedidoItem-2-5']").fill("1")

    page.once("dialog", _aceitar_confirmacao)
    ctx.get_by_role("button", name="Confirmar").click()
    aguardar_ajax_global(page)
    ctx.get_by_role("button", name="Confirmar").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)
    

def _aceitar_confirmacao(dialog) -> None:
    logger.info("Caixa de diálogo capturada: {}", dialog.message)
    dialog.accept()
    logger.info("Diálogo aceito.")