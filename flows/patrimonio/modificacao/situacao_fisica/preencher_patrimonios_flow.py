from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global
from flows.patrimonio.shared.consultar_bem_flow import consultar_bem


def preencher_patrimonios(page: Page, ug: dict[str, str], bem: dict[str, str]) -> bool:
    logger.info("Iniciou preenchimento de patrimônios {}.", bem["nome"])

    ctx = escopo(page)

    ctx.locator("button[name='lookup-cdBemPerm-1-3']").click()
    aguardar_ajax_global(page)

    existe_bem = consultar_bem(page, ug, bem)

    if not existe_bem:
        logger.info("Nenhum bem com nome '{}' encontrado para seleção.", bem["nome"])
        return False

    logger.info("Finalizou preenchimento de patrimônios {}.", bem["nome"])
    return True
