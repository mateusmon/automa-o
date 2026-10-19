from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_patrimonio
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def preencher_bens_transferidos(page: Page, funcionario: dict[str, str]) -> None:
    data_hoje = obter_data_patrimonio(page, "DDMMYYYY")

    logger.info("Iniciou o preenchimento dos dados dos bens. Data de recebimento: '{}', Recebedor: '{}'.", data_hoje, funcionario["nome"])

    ctx = escopo(page)

    ctx.type("input[name='dtRecebimento-1-5']", data_hoje, delay=50)

    # Esta gambiarra é necessária devido a um bug do ASI. O preencher_autocomplete não funciona aqui
    field_responsavel = ctx.locator("input[name='recebedor-1-6']")
    field_responsavel.click()
    field_responsavel.type(funcionario["nome"], delay=50)
    aguardar_ajax_global(page)
    field_responsavel.press("ArrowDown")
    field_responsavel.press("ArrowDown")
    field_responsavel.press("Enter")

    if ctx.locator("input[name='consertado-1-7']").is_enabled():
        ctx.click("input[name='consertado-1-7']")

    campo_valor_conserto = ctx.locator("input[name='vlConserto-1-8']")

    if campo_valor_conserto.is_visible() and campo_valor_conserto.is_editable():
        campo_valor_conserto.dblclick()
        campo_valor_conserto.type("10")

    ctx.click("button[name='submitFinish']")
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou o preenchimento dos dados dos bens para o recebedor '{}'.", funcionario["nome"])
