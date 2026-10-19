from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global
from flows.patrimonio.shared.consultar_bem_flow import consultar_bem


def selecionar_bem(page: Page, ug: dict[str, str], bem: dict[str, str]) -> bool:
    logger.info("Iniciou seleção de bens com a UG: '{}'.", ug["codigo"])

    ctx = escopo(page)

    ctx.locator("button[name='lookup-cdBemPerm-1-3']").click()
    aguardar_ajax_global(page)
    numero_patrimonio = consultar_bem(page, ug, bem)

    if not numero_patrimonio:
        logger.info("Não há patrimônio para fazer seleção com a UG: '{}'.", ug["codigo"])
        return False
    
    aguardar_ajax_global(page)

    logger.info("Finalizou seleção de bens com a UG: '{}'.", ug["codigo"])
    return True
