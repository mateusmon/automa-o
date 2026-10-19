from datetime import date

from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def consultar_selecao_bens(page: Page, ug: dict[str, str]) -> None:
    logger.info("Iniciou consulta de seleção de bens com a UG: '{}'.", ug["codigo"])

    # Foi necessário preencher o campo de data, pois eram exibidas todas as opções, em vez de apenas a que criamos.
    
    # O campo de data é desabilitado na inclusão da Seleção de Bens (gravando com a data atual).
    # Por isso, a consulta filtra pela data civil atual para encontrar os registros recém-criados.
    data_hoje = date.today().strftime("%d/%m/%Y")

    ctx = escopo(page)

    ctx.get_by_role("button", name="Consulta", exact=True).click()
    aguardar_ajax_global(page)

    preencher_campo(ctx, "input[name='model-1']", ug["codigo"])
    aguardar_ajax_global(page)
    logger.info("Filtrando seleção de bens pela UG: '{}'.", ug["codigo"])
    ctx.locator("input[name='model-4-from']").fill(data_hoje)
    ctx.locator("input[name='model-4-to']").click()

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de seleção de bens com a UG: '{}'.", ug["codigo"])
