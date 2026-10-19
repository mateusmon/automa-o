from datetime import datetime, timedelta
from loguru import logger

from playwright.sync_api import Page, expect

from utils.competencia_financeira import obter_data_patrimonio
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, clicar_com_ajax, preencher_campo


def consultar_bem(page: Page, ug: dict[str, str], bem: dict[str, str]) -> None:
    logger.info("Iniciou consulta de bem patrimonial '{}' na UG '{}'.", bem["nome"], ug["nome"])
    ctx = escopo(page)

    campo_ug = ctx.locator("input[name='model-3']")
    campo_material = ctx.locator("input[name='model-15']")

    if campo_ug.is_visible():
        logger.info("Preenchendo código da UG: '{}'.", ug["codigo"])
        preencher_campo(ctx, campo_ug, ug["codigo"])
        aguardar_ajax_global(page)

    try:
        expect(campo_material).to_be_visible()
        logger.info("Preenchendo nome do material: '{}'.", bem["nome"])
        preencher_campo(ctx, campo_material, bem["nome"])
        aguardar_ajax_global(page)
    except RuntimeError:
        raise RuntimeError("Falha ao tentar preencher campo de material") 

    data_inicio, data_fim = obter_datas(page)
    logger.info("Preenchendo período de consulta: de '{}' até '{}'.", data_inicio, data_fim)
    ctx.locator("input[name='model-18-from']").fill(data_inicio)
    ctx.locator("input[name='model-18-to']").dblclick()
    ctx.locator("input[name='model-18-to']").fill(data_fim)

    clicar_com_ajax(ctx, "button[name='submitSearch']")

    logger.info("Finalizou consulta de bem patrimonial '{}' na UG '{}'.", bem["nome"], ug["nome"])


def obter_datas(page: Page) -> tuple[str, str]:
    hoje_str = obter_data_patrimonio(page, formato="DD/MM/YYYY")
    hoje_dt = datetime.strptime(hoje_str, "%d/%m/%Y")
    
    mes_passado_str = (hoje_dt - timedelta(days=30)).strftime("%d/%m/%Y")
        
    return mes_passado_str, hoje_str
