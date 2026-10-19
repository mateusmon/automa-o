from playwright.sync_api import Page
from loguru import logger

from flows.patrimonio.shared.consultar_bem_flow import consultar_bem
from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def preencher_itens(page: Page, ug: dict[str, str], bem: dict[str, str]) -> bool:
    logger.info("Iniciou preenchimento de itens para a unidade gestora '{}'.", ug["nome"])

    ctx = escopo(page)

    ctx.locator("button[name='lookup-cdBemPerm-1-3']").click()
    aguardar_ajax_global(page)

    numero_patrimonio = consultar_bem(page, ug, bem)

    if not numero_patrimonio:
        logger.info("Não há bens para seleção para a unidade gestora '{}'.", ug["nome"])
        return False

    logger.info("Finalizou preenchimento de itens para a unidade gestora '{}'.", ug["nome"])
    return True
