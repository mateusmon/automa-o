from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro
from flows.patrimonio.shared.consultar_bem_flow import consultar_bem


def preencher_bem(page: Page, ug_data: dict[str, str], bem: dict[str, str]) -> bool:
    logger.info("Iniciou preenchimento de bem {}.", bem["nome"])

    ctx = escopo(page)

    ctx.locator("button[name='lookup-itens-1-3']").click()
    aguardar_ajax_global(page)

    achou_bem = consultar_bem(page, ug_data, bem)

    if not achou_bem:
        logger.info("Nenhum bem encontrado para seleção {}.", bem["nome"])
        return False
    logger.info("Bem encontrado para seleção.")
    ctx.locator("input[name='itens-1-6']").fill(bem["preco_unitario"])
    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou preenchimento de bem {}.", bem["nome"])
    return True
