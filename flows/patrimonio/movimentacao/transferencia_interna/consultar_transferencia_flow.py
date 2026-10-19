from playwright.sync_api import Page, Frame
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo, clicar_com_ajax


def consultar_transferencia(page: Page, ug: dict[str, str], ul_origem: dict[str, str], ul_destino: dict[str, str], selecionar: bool = False, estoque: bool = True) -> bool:

    logger.info("Iniciou consulta de transferência interna.")

    ctx = escopo(page)

    clicar_com_ajax(ctx, ctx.get_by_role("button", name="Consulta", exact=True))
    preencher_campo(ctx, "input[name='model-2']", ug["codigo"])
    if estoque:
        selecionar_ul_estoque(ctx, page, ul_origem)
    else:
        preencher_campo(ctx, "input[name='model-4']", ul_origem["sigla"])
    preencher_campo(ctx, "input[name='model-7']", ul_destino["sigla"])
    clicar_com_ajax(ctx, "button[name='submitSearch']")

    if selecionar:
        span_resultado = ctx.locator("span[name='searchResultSize']")
        span_resultado.wait_for(state="visible")

        if span_resultado.inner_text() == "0":
            logger.debug("Total de itens consultados: {}", span_resultado.inner_text())
            return False
        
        linha = ctx.locator("table[name='paginationTable'] tbody tr").first
        linha.locator("button[name='submitUse']").click()

    logger.info("Finalizou consulta de transferência interna.")
    return True


def selecionar_ul_estoque(ctx: Frame | Page, page: Page, ul_origem: dict[str, str]) -> None:
    """Seleciona a UL de estoque através da modal de busca por código.

    Nota: Esta é a maneira mais precisa de selecionar a UL de estoque para evitar
    ambiguidade quando o código aparece em qualquer parte do nome de outras unidades.
    """

    ctx.locator("button[name='lookup-model-4']").click()
    aguardar_ajax_global(page)

    ctx.locator("input[name='model-4-from']").fill(ul_origem["codigo"])
    ctx.locator("input[name='model-4-to']").click()

    clicar_com_ajax(ctx, "button[name='submitSearch']")

    linha = ctx.locator("table[name='paginationTable'] tbody tr")
    clicar_com_ajax(ctx, linha.first.locator("button[name='submitUse']"))
