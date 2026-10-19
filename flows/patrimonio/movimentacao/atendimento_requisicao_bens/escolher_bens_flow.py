from playwright.sync_api import Page
from loguru import logger

from flows.patrimonio.shared.consultar_bem_flow import consultar_bem
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def escolher_bens(page: Page, ug: dict[str, str], bem: dict[str, str]) -> bool:
    logger.info("Iniciou a seleção de bens para a UG '{}'.", ug["sigla"])

    ctx = escopo(page)

    ctx.locator("button[name='edit-itens-1-7']").click()
    aguardar_ajax_global(page)

    ctx.locator("button[name='lookup-cdBemPerm-1-3']").click()
    aguardar_ajax_global(page)

    ha_requisicoes = consultar_bem(page, ug, bem)

    if not ha_requisicoes:
        logger.info("Nenhum bem com nome '{}' encontrado para seleção.", bem["nome"])
        return False
    
    ctx.locator("button[name='submitBack']").click()
    aguardar_ajax_global(page)

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)
    
    logger.info("Finalizou a seleção de bens para a UG '{}'.", ug["sigla"])
    return True
