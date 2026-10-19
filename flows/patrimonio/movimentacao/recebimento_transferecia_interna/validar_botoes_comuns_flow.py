from loguru import logger
from playwright.sync_api import Page, expect

from utils.versao import escopo
from utils.waits import clicar_com_ajax


def validar_botoes_comuns(page: Page) -> None:
    logger.info("Iniciou validação dos botões.")

    ctx = escopo(page)

    clicar_com_ajax(ctx, "button[name='submitView']")
    ctx.wait_for_timeout(timeout=3_000)
    clicar_com_ajax(ctx, "button[name='submitBack']")

    clicar_com_ajax(ctx, "button[name='submitPrint']")
    expect(ctx.get_by_text("Relatórios", exact=True)).to_be_visible()
    clicar_com_ajax(ctx, "button[name='submitBack']")

    clicar_com_ajax(ctx,"input[name='transferenciaAceitaNo'][value='false']")
    clicar_com_ajax(ctx, "input[name='opcaoPatrAnt'][value='S']")
    clicar_com_ajax(ctx, "button[name='submitRestore']")

    clicar_com_ajax(ctx, "button[name='submitSearch']")
    ctx.wait_for_timeout(timeout=3_000)
    clicar_com_ajax(ctx, "button[name='submitCancel']")

    clicar_com_ajax(ctx, "button[name='submitBack']")

    logger.info("Finalizou validação dos botões.")