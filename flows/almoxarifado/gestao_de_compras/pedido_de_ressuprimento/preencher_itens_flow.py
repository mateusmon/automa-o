from loguru import logger
from playwright.sync_api import Page, expect

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo, esperar_sucesso_ou_erro


def preencher_itens(page: Page, material: dict) -> None:
    logger.info("Iniciou preenchimento de itens de cadastro de ressuprimento para material '{}'.", material['nome'])

    ctx = escopo(page)
    _preencher(ctx, page, material)

    logger.info("Finalizou preenchimento de itens de cadastro de ressuprimento para material '{}'.", material['nome'])


def _preencher(ctx, page: Page, material: dict) -> None:
    nome_completo = f"{material['nome']} {material['complemento']}"

    ctx.get_by_role("button", name="Itens").click()
    aguardar_ajax_global(page)

    expect(
        ctx.get_by_role("heading", name="Itens da entrada")
    ).to_be_visible()

    logger.info("Preenchendo material '{}'.", nome_completo)
    preencher_campo(ctx, "input[name='bemServico-1-3']", nome_completo)
    aguardar_ajax_global(page)

    logger.info("Preenchendo quantidade pedida '1'.")
    ctx.locator("input[name='qtPedido-1-10']").fill("1")
    aguardar_ajax_global(page)

    page.once("dialog", _aceitar_confirmacao)
    ctx.get_by_role("button", name="Confirmar").click()
    aguardar_ajax_global(page)

    esperar_sucesso_ou_erro(ctx)


def _aceitar_confirmacao(dialog) -> None:
    logger.info("Caixa de diálogo capturada: {}", dialog.message)
    dialog.accept()
    logger.info("Diálogo aceito.")
