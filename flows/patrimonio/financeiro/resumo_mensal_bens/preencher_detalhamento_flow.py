
from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_patrimonio
from utils.versao import escopo
from utils.waits import clicar_com_ajax, esperar_sucesso_ou_erro, preencher_campo


def preencher_detalhamento(page: Page, ug_data: dict[str, str]) -> None:
    ano_atual, mes_atual = obter_data_patrimonio(page, "YYYY/MM").split("/")
    ano_anterior = str(int(ano_atual)-1)
    
    # Isso será usado somente se o mês atual for janeiro
    if mes_atual == "01":
        data_inicial = f"{ano_anterior}01"
        data_final = f"{ano_anterior}12"
    else:
        data_inicial = ano_atual + "01"
        data_final = f"{ano_atual}{mes_atual}"
    
    logger.info("Iniciou o preenchimento do detalhamento na UG '{}'.", ug_data["nome"])

    ctx = escopo(page)

    logger.info("Preenchendo código da UG: '{}'.", ug_data["codigo"])
    preencher_campo(ctx, "input[name='ugs-1-1']", ug_data["codigo"])

    logger.info("Preenchendo período de detalhamento: '{}' até '{}'.", data_inicial, data_final)
    ctx.type("input[name='ugs-1-3']", data_inicial, delay=50)
    ctx.type("input[name='ugs1-1-3']", data_final, delay=50)
    
    botao_confirmar = ctx.locator("button[name='submitFinish']")
    clicar_com_ajax(ctx, botao_confirmar)
    esperar_sucesso_ou_erro(ctx)
    
    logger.info("Finalizou o preenchimento do detalhamento na UG '{}'.", ug_data["nome"])
