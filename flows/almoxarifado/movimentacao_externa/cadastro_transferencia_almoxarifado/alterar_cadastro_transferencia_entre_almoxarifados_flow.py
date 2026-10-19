from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def alterar_cadastro_transferencia_entre_almoxarifados(page: Page) -> bool:
    logger.info("Iniciou alteração de cadastro de transferência entre almoxarifados.")

    ctx = escopo(page)

    campo_qtd_requisicao = ctx.locator("input[name='qtRequisicao-1-5']")
    if campo_qtd_requisicao.is_disabled():
        logger.info("Campo de quantidade desabilitado. Não é possível fazer alteração.")
        return False

    quantidade = campo_qtd_requisicao.input_value()

    if quantidade == "1":
        nova_quantidade = "2"
    else:
        nova_quantidade = "1"

    logger.info("Alterando quantidade de requisição: '{}' -> '{}'.", quantidade, nova_quantidade)
    ctx.locator("input[name='qtRequisicao-1-5']").fill(nova_quantidade)

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou alteração de cadastro de transferência entre almoxarifados.")
    return True
