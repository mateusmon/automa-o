from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_patrimonio
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo


def preencher_dados_gerais(page: Page, ul: dict[str, str]) -> None:
    logger.info("Iniciou o preenchimento dos dados gerais.")

    endereco = ul["endereco"]

    data = obter_data_patrimonio(page, formato="DDMMYYYY")

    ctx = escopo(page)

    ctx.locator("input[name='exigeAssinatura'][value='true']").check()
    aguardar_ajax_global(page)

    preencher_campo(ctx, "input[name='ulDestino']", endereco)

    campo_retorno = ctx.locator("input[name='dtPrevRetorno']")

    if campo_retorno.is_visible() and campo_retorno.is_enabled():
        campo_retorno.type(data, delay=50)

    data_trans = ctx.locator("input[name='dtTransferencia']")
    if data_trans.is_visible() and data_trans.is_enabled():
        data_trans.dblclick()
        data_trans.type(data, delay=50)

    logger.info("Finalizou o preenchimento dos dados gerais.")
