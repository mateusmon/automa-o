from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo

def consultar_recebimento_termo_responsabilidade(page: Page, ug: dict[str, str]) -> None:
    logger.info("Consultando Recebimento do Termo de Responsabilidade.")

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    # Preenche U.G.
    preencher_campo(ctx, "input[name='model-1']", ug["codigo"])

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    # Selecionar Recebimento de Termo de Responsabilidade
    linha = ctx.locator("table[name='paginationTable'] tbody tr").filter(
        has=ctx.locator("td").nth(0).filter(
            has_text=ug["nome"]
        )
    ).first

    if linha.count() == 0:
        logger.info("Nenhuma Termo de Responsabilidade encontrada para a UG '{}'.", ug["nome"])
        return False
    
    linha.locator("button[name='submitUse']").click()

    logger.info("Recebimento do Termo de Responsabilidade consultado.")

    return True