from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo


def preencher_dados_gerais_almoxarifado(page: Page, almoxarifado: dict, ug: dict) -> None:
    """
    Preenche os dados gerais do Almoxarifado e confirma o cadastro.

    Cenário A: os mesmos seletores valem para v3 e v4; a única diferença é o
    escopo (page na v3, iframe na v4), resolvido por `escopo(page)`.

    Campos:
    - Nome (`dsAlmoxarifado`) — obrigatório;
    - Sigla (`sgAlmoxarifado`) — é a chave usada na consulta/exclusão;
    - Controle financeiro (`inControleFin=S`) — já vem em "Sim"; marcado
      explicitamente para determinismo;
    - U.G. (`cdUg`) — lookup obrigatório.

    O Órgão vem pré-preenchido pelo sistema (varia por cliente) e o Código é
    gerado; nenhum dos dois é tocado aqui.

    :param almoxarifado: dict do blueprint com nome e sigla.
    :param ug: dict da U.G. do cliente (contexto_cliente.ug()); usa a sigla.
    """
    logger.info("Iniciou preenchimento de dados gerais de Almoxarifado ' {}'.", almoxarifado["sigla"])

    ctx = escopo(page)

    aguardar_ajax_global(page)
    ctx.locator("input[name='dsAlmoxarifado']").wait_for(state="visible")
    logger.info("Preenchendo Nome de Almoxarifado: '{}'.", almoxarifado["nome"])
    ctx.locator("input[name='dsAlmoxarifado']").fill(almoxarifado["nome"])
    logger.info("Preenchendo Sigla de Almoxarifado: '{}'.", almoxarifado["sigla"])
    ctx.locator("input[name='sgAlmoxarifado']").fill(almoxarifado["sigla"])

    ctx.locator("input[name='inControleFin'][value='S']").check()
    aguardar_ajax_global(page)

    preencher_campo(ctx, "input[name='cdUg']", ug["codigo"])

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou preenchimento de dados gerais de Almoxarifado ' {}'.", almoxarifado["sigla"])
