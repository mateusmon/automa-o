from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_patrimonio
from utils.versao import escopo
from utils.waits import preencher_campo


def preencher_dados_gerais_completo(page: Page, ug_data: dict[str, str], funcionario: dict[str, str], fornecedor: dict[str, str]) -> None:
    logger.info("Iniciou o preenchimento de dados gerais da Transferência Externa para '{}'.", fornecedor["nome"])

    ctx = escopo(page)
    data = obter_data_patrimonio(page, formato="DD/MM/YYYY")

    logger.info("Preenchendo código da UG: '{}'.", ug_data["codigo"])
    ctx.locator("input[name='ug']").clear()
    preencher_campo(ctx, "input[name='ug']", ug_data["codigo"])

    logger.info("Preenchendo nome do responsável: '{}'.", funcionario["nome"])
    ctx.locator("input[name='funAutorizSaida']").clear()
    preencher_campo(ctx, "input[name='funAutorizSaida']", funcionario["nome"])

    logger.info("Preenchendo nome do fornecedor: '{}'.", fornecedor["nome"])
    ctx.locator("input[name='fornecedor']").clear()
    preencher_campo(ctx, "input[name='fornecedor']", fornecedor["nome"])

    logger.info("Preenchendo data da Transferência: '{}'.", data)
    campo_data = ctx.locator("input[name='dtTransferencia']")
    campo_data.clear()
    campo_data.fill(data)

    logger.info("Preenchendo data prevista de retorno: '{}'.", data)
    campo_prev_retorno = ctx.locator("input[name='dtPrevRetorno']")
    campo_prev_retorno.clear()
    logger.info("Preenchendo data prevista de retorno: '{}'.", data)   
    campo_prev_retorno.fill(data)

    ctx.locator("input[name='portador']").clear()
    preencher_campo(ctx, "input[name='portador']", "   ")

    logger.info("Finalizou o preenchimento de dados gerais da Transferência Externa para '{}'.", fornecedor["nome"])