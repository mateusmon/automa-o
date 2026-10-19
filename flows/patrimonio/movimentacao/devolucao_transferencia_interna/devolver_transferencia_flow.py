from typing import Any

from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_patrimonio
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def devolver_transferencia(page: Page, ul: dict[str, Any]) -> None:
    logger.info("Iniciou devolução da transferência interna para a UL '{}'.", ul["sigla"])

    ctx = escopo(page)

    nome_responsavel = ul["responsavel"]["nome"]

    date = obter_data_patrimonio(page, "DDMMYYYY")

    ctx.locator("input[name='dtRecebimento-1-5']").type(date, delay=50)

    # Esta gambiarra é necessária devido a um bug do ASI. O preencher_autocomplete não funciona aqui
    field_responsavel = ctx.locator("input[name='recebedor-1-6']")
    field_responsavel.click()
    field_responsavel.type(nome_responsavel, delay=50)
    aguardar_ajax_global(page)
    field_responsavel.press("ArrowDown")
    field_responsavel.press("ArrowDown")
    field_responsavel.press("Enter")

    campo_objetivo = ctx.locator("input[name='motivoSaidaTemp']")
    campo_valor_conserto = ctx.locator("input[name='vlConserto-1-8']")

    if campo_objetivo.input_value() == "CONSERTO":
        ctx.locator("input[name='consertado-1-7']").click()
        campo_valor_conserto.dblclick()
        campo_valor_conserto.fill("100,00")

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou devolução da transferência interna para a UL '{}'.", ul["sigla"])
