from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def preencher_dados_gerais(page: Page, almoxarifado: dict, ua: dict, tipo: str) -> bool:
    logger.info("Iniciou preenchimento de dados gerais do inventário no almoxarifado '{}'.", almoxarifado["sigla"])

    responsavel = ua["responsavel"]
    ctx = escopo(page)

    logger.info("Preenchendo sigla do almoxarifado '{}'.", almoxarifado["sigla"])
    preencher_campo(ctx, "input[name='cdAlmoxarifado']", almoxarifado["sigla"])

    try:
        logger.info("Preenchendo tipo de inventário '{}'.", tipo)
        preencher_campo(ctx, "input[name='cdTipoInventario']", tipo)
    except RuntimeError:
        logger.warning("Este cliente não possui inventário do tipo {}.", tipo)
        return False

    logger.info("Preenchendo descrição do inventário 'Descrição do inventário'.")
    ctx.locator("textarea[name='dsFinalidade']").fill("Descrição do inventário.")

    logger.info("Preenchendo nome do responsável pelo inventário '{}'.", responsavel["nome"])
    preencher_campo(ctx, "input[name='nmFuncionario-1-4']", responsavel["nome"])
    ctx.locator("input[name='sqInvResponsavel']").click()

    ctx.locator("button[name='submitTabItens']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou preenchimento de dados gerais do inventário no almoxarifado '{}'.", almoxarifado["sigla"])
    return True
