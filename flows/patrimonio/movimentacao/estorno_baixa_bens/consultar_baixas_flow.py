import re
from datetime import datetime, timedelta

from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_patrimonio
from utils.versao import escopo
from utils.waits import aguardar_ajax_global

DIAS_MINIMOS_PARA_ESTORNO = 31

def consultar_baixas(page: Page, ug: dict[str, str]) -> bool:
    logger.info("Consultando se há baixas válidas para estorno.")

    ctx = escopo(page)

    data_base = obter_data_patrimonio(page, formato="DD/MM/YYYY")
    dt_base_obj = datetime.strptime(data_base, "%d/%m/%Y")
    limite = dt_base_obj - timedelta(days=DIAS_MINIMOS_PARA_ESTORNO)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)
    logger.info("Preenchendo campo de UG (model-2) com o código da UG: '{}'.", ug["codigo"])
    ctx.locator("input[name='model-2']").fill(ug["codigo"])
    ctx.locator("button[name='lookup-model-2']").click()
    aguardar_ajax_global(page)
    logger.info("Preenchendo campo de Data de Baixa (model-9) com o valor mínimo para estorno: '{}'.", limite.strftime("%d/%m/%Y"))
    ctx.locator("input[name='model-9-to']").fill(limite.strftime("%d/%m/%Y"))

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    linha = ctx.locator("table[name='paginationTable'] tbody tr").filter(
        has=ctx.locator("td").nth(0).filter(
            has_text=ug["nome"]
        )
    ).filter(
        has=ctx.locator("td").nth(4).filter(
            has_text=re.compile(r"^\s*$")
        )
    ).first

    if linha.count() == 0:
        logger.info("Não tem nenhuma baixa válida para estorno.")
        return False

    linha.locator("button[name='submitUse']").click()
    aguardar_ajax_global(page)

    logger.info("Consulta finalizada.")

    return True
