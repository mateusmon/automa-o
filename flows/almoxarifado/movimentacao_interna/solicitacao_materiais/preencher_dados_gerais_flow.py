from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_almoxarifado
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def preencher_dados_gerais(page: Page, almoxarifado: dict, ur: dict, material: dict, quantidade: str = "1") -> None:
    logger.info("Iniciou preenchimento de dados gerais da solicitação de materiais no almoxarifado '{}'.", almoxarifado["nome"])

    ctx = escopo(page)
    _preencher_campos(ctx, page, almoxarifado, ur, material, quantidade)

    logger.info("Finalizou preenchimento de dados gerais da solicitação de materiais no almoxarifado '{}'.", almoxarifado["nome"])


def _preencher_campos(ctx, page: Page, almoxarifado: dict, ur: dict, material: dict, quantidade: str) -> None:
    ctx.get_by_role("button", name="Confirmar").wait_for(state="visible")
    logger.info("Preenchendo sigla do almoxarifado: '{}'.", almoxarifado["sigla"])
    preencher_campo(ctx, "input[name='almoxarifado']", almoxarifado["sigla"])
    aguardar_ajax_global(page)
    logger.info("Preenchendo nome da UR: '{}'.", ur["nome"])
    preencher_campo(ctx, "input[name='ur']", ur["nome"])
    aguardar_ajax_global(page)
    logger.info("Preenchendo nome do material: '{}'.", material["nome"])
    preencher_campo(ctx, "input[name='CatalogoMat-1-3']", material["nome"], lookup_name='lookup-catalogoMat-1-3')
    aguardar_ajax_global(page)
    data = obter_data_almoxarifado(page, "DDMMYYYY")
    logger.info("Preenchendo data da solicitação: '{}'.", data)
    ctx.locator("input[name='dtSolicitacao']").clear()
    ctx.locator("input[name='dtSolicitacao']").type(data, delay=50)

    logger.info("Preenchendo quantidade solicitada: '{}'.", quantidade)
    field_quantidade = ctx.locator("input[name='qtSolicitacao2-5']")
    field_quantidade.dblclick()
    field_quantidade.type(quantidade, delay=50)
    aguardar_ajax_global(page)
