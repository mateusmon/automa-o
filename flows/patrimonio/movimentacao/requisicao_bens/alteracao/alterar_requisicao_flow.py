from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def alterar_requisicao(page: Page) -> bool:
    logger.info("Iniciou alteração de Requisição.")

    ctx = escopo(page)

    situacao = ctx.locator("input[name='cdTpSituacaoReq']").input_value()

    if situacao == "ATENDIDA":
        logger.info("Requisição já foi atendida, não é possível fazer a alteração.")
        return False

    campo = ctx.locator("input[name='qtRequisicao-1-4']")

    if campo.input_value() == "1":
        valor = "2"
    else:
        valor = "1"
    logger.info("Alterando a quantidade da Requisição: '{}' -> '{}'.", campo.input_value(), valor)
    campo.fill(valor)
    ctx.locator("button[name='submitFinish']").click()
    
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)
    
    logger.info("Finalizou alteração de Requisição. Quantidade alterada para '{}'.", valor)
    return True
