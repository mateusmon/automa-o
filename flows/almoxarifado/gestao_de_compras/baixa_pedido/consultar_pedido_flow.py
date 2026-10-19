from loguru import logger
from playwright.sync_api import Page

from utils.inputs import clicar_botao_com_retry
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def consultar_pedido(page: Page, ua_data: dict[str, str]) -> None:
    logger.info("Iniciou consulta de pedido de compra na UA '{}'.", ua_data["sigla"])

    ctx = escopo(page)

    botao_lookup = ctx.locator("button[name='lookup-pedido']")
    botao_lookup.wait_for(state="visible")
    alvo_esperado = ctx.locator("td.textoLookup", has_text="Unidade Administrativa:")
    clicar_botao_com_retry(page, botao_lookup, alvo_esperado)

    aguardar_ajax_global(page)

    campo_ua = (
        ctx.locator("table[name='paginationTable'] tbody tr")
        .filter(has_text="Unidade Administrativa")
        .locator("input[type='text']")
    )

    if campo_ua.is_visible():
        logger.info("Preenchendo UA '{}'.", ua_data["sigla"])
        preencher_campo(ctx, campo_ua, ua_data["sigla"])

    campo_solicitante = (
        ctx.locator("table[name='paginationTable'] tbody tr")
        .filter(has_text="Solicitante")
        .locator("input[type='text']")
    )

    usuario_v3 = ctx.locator("a[class='userName']")
    usuario_v4 = page.locator("button[title='Usuário']")

    if usuario_v3.is_visible():
        funcionario_solicitante = usuario_v3.inner_text()
    elif usuario_v4.is_visible():
        usuario_v4.click()
        funcionario_solicitante = page.locator("p[class='descUser']").first.inner_text()
        page.locator("button[class='close transition-scale']").click()

    logger.info("Preenchendo funcionário solicitante '{}'.", funcionario_solicitante)
    preencher_campo(ctx, campo_solicitante, funcionario_solicitante)
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de pedido de compra na UA '{}'.", ua_data["sigla"])
