from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def alterar_quantidade(page: Page) -> None:
    logger.info("Iniciou alteração de requisição.")

    ctx = escopo(page)

    linha = ctx.locator("table.tabela tbody[name='tboItens'] tr").first
    td = linha.locator("td")
    quantidade_td = td.count()
    quantidade_solicitada =  ctx.locator(f"input[name='qtRequisicao-2-{quantidade_td-3}']").input_value()

    if quantidade_solicitada == "2":
        nova_quantidade = "1"
    else:
        nova_quantidade = "2"

    logger.info("Alterando quantidade de requisição: '{}' -> '{}'.", quantidade_solicitada, nova_quantidade)
    ctx.locator(f"input[name='qtRequisicao-2-{quantidade_td-3}']").fill(nova_quantidade)

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)
    
    logger.info("Finalizou alteração de requisição.")
