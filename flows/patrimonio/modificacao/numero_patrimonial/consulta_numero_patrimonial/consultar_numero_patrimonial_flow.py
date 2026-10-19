from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def consultar_numero_patrimonial(page: Page, ug: dict[str, str]) -> bool:
    logger.info("Iniciou consulta de modificação do número patrimonial")

    ctx = escopo(page)

    botao_consulta = ctx.locator("button[name='submitSearch']")

    if botao_consulta.is_disabled():
        logger.warning("Botão de consulta está desabilitado.")
        return False
    
    botao_consulta.click()
    aguardar_ajax_global(page)

    preencher_campo(ctx, "input[name='model-1']", ug["codigo"])

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou consulta de modificação do número patrimonial")

    return True
