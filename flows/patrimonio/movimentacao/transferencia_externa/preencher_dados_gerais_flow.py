from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_patrimonio
from utils.versao import escopo
from utils.waits import preencher_campo


def preencher_dados_gerais(page: Page, ug_data: dict[str, str], fornecedor_data: dict[str, str], funcionario: dict[str, str]) -> None:
    logger.info("Iniciou o preenchimento dos dados gerais.")

    ctx = escopo(page)

    data = obter_data_patrimonio(page, formato="DD/MM/YYYY")

    ug = ug_data["codigo"]
    fornecedor = fornecedor_data["nome"]
    nome_funcionario = funcionario["nome"]

    preencher_campo(ctx, "input[name='ug']", ug)

    campo_responsavel = ctx.locator("input[name='funAutorizSaida']")

    if campo_responsavel.input_value() == "":
        preencher_campo(ctx, "input[name='funAutorizSaida']", nome_funcionario)

    preencher_campo(ctx, "input[name='fornecedor']", fornecedor)

    if ctx.locator("input[name='portador']").is_visible():
        preencher_campo(ctx, "input[name='portador']", "   ")

    ctx.locator("input[name='dtPrevRetorno']").clear()
    ctx.locator("input[name='dtTransferencia']").clear()
    logger.info("Preenchendo data da transferência: '{}'.", data)
    ctx.locator("input[name='dtTransferencia']").fill(data)
    logger.info("Preenchendo data prevista de retorno: '{}'.", data)
    ctx.locator("input[name='dtPrevRetorno']").fill(data)
    
    logger.info("Finalizou o preenchimento dos dados gerais.")
