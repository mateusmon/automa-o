from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_patrimonio
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo


def preencher_novos_responsaveis(page: Page, ul: dict[str, dict]) -> None:
    responsavel = ul["responsavel"]

    logger.info("Iniciou o preenchimento dos novos responsáveis {}.", responsavel["nome"])

    ctx = escopo(page)
    data = obter_data_patrimonio(page, formato="DD/MM/YYYY")

    preencher_campo(ctx, "input[name='funcionario-1-1']", responsavel["nome"])
    preencher_campo(ctx, "input[name='tipoFuncao-1-2']", responsavel["funcao"])

    ctx.locator("input[name='inAssinatura-1-4']").check()
    logger.info("Preenchendo campo de Data de Início com valor obtido da competência patrimonial '{}'.", data)
    ctx.locator("input[name='dtInicio-1-5']").fill(data)

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou o preenchimento dos novos responsáveis {}.", responsavel["nome"])
