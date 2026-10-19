from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global
from flows.patrimonio.shared.consultar_bem_flow import consultar_bem


def preencher_bens_transferir(page: Page, ug: dict[str, str], material: dict[str, str]) -> bool | str:
    logger.info("Iniciou o preenchimento dos bens para transferência.")

    ctx = escopo(page)
    
    ctx.locator("button[name='submitTabItens']").click()
    aguardar_ajax_global(page)

    ctx.locator("button[name='lookup-cdBemPerm-1-3']").click()
    aguardar_ajax_global(page)
    
    encontrou_bem = consultar_bem(page, ug, material)
    
    if not encontrou_bem:
        logger.info("Bem não encontrado.")
        return False

    aguardar_ajax_global(page)

    logger.info("Finalizou o preenchimento dos bens para transferência.")
    return True
