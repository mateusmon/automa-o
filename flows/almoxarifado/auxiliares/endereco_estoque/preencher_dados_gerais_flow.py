from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo


def preencher_dados_gerais(page: Page, almoxarifado: dict, endereco: str) -> None:
    logger.info("Preenchendo dados gerais.")

    sigla_almoxarifado = almoxarifado["sigla"]

    ctx = escopo(page)

    logger.info("Preenchendo sigla do almoxarifado '{}'.", sigla_almoxarifado)
    preencher_campo(ctx, "input[name='almoxarifado']", sigla_almoxarifado)
    
    campo_codigo = ctx.locator("input[name='cdEndereco']")
    if campo_codigo.is_enabled():
        campo_codigo.type(endereco, delay=50)

    # Descrição
    logger.info("Preenchendo descrição do endereço de estoque '{}'.", endereco)
    ctx.locator("input[name='dsEnderecoEst']").type(endereco, delay=50)
    # Siglas
    logger.info("Preenchendo sigla do endereço de estoque '{}'.", endereco)
    ctx.locator("input[name='sgEnderecoEst']").type(endereco, delay=50)    

    # Checando a checkbox de "último nível"
    ctx.locator("input[name='idUltNivel']").check()

    logger.info("Preenchimento de dados gerais finalizado.")

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)
