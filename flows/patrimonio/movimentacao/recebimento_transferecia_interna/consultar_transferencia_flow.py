from loguru import logger
from playwright.sync_api import Page, expect

from utils.competencia_financeira import obter_data_patrimonio
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, clicar_com_ajax, preencher_campo


def consultar_transferencia(page: Page, ug: dict[str, str], verificar: bool = False) -> None:

    logger.info("Iniciou consulta da transferência interna. UG: '{}'.", ug["codigo"])

    ctx = escopo(page)

    data = obter_data_patrimonio(page)

    if verificar:
        # Verificar os botões Cancelar e Restaurar
        clicar_com_ajax(ctx, "button[name='submitCancel']")
        expect(ctx.get_by_role("heading", name="Recebimento", exact=True)).to_be_visible()
        clicar_com_ajax(ctx, "button[name='submitSearch']")

        preencher_campo(ctx, "input[name='model-2']", ug["codigo"])
        clicar_com_ajax(ctx, "button[name='submitRestore']")

    preencher_campo(ctx, "input[name='model-2']", ug["codigo"])
    aguardar_ajax_global(page)

    ctx.locator("input[name='model-9-from']").fill(data)
    clicar_com_ajax(ctx, "input[name='model-9-to']")
    
    clicar_com_ajax(ctx, "button[name='submitSearch']")

    logger.info("Finalizou consulta da transferência interna. UG: '{}'.", ug["codigo"])
