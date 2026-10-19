from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_patrimonio
from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def selecionar_bem(page: Page, ul: dict[str, str]):
    logger.info("Selecionando bem para a UL '{}'.", ul["sigla"])

    ctx = escopo(page)

    data = obter_data_patrimonio(page, formato="DDMMYYYY")

    if ctx.locator("button[name='submitBack']").is_visible():
        ctx.locator("button[name='submitBack']").click()
        aguardar_ajax_global(page)

    rows = ctx.locator("table.tabela").first.locator("tbody tr")
    count = rows.count()

    if count == 0:
        logger.info(
            "Nenhum bem encontrado para a UL '{}'.", ul["sigla"]
        )
        logger.info("Pulando teste.")
        return False
    
    rows.first.locator("button[name='submitUse']").click()
    aguardar_ajax_global(page)

    linhas_bens = ctx.locator("tbody tr.keeporder")
    total_linhas = linhas_bens.count()

    for i in range(total_linhas):
        linha = linhas_bens.nth(i)
        campo_patrimonio = linha.locator("input[name^='cdBemPerm-']")
        
        if campo_patrimonio.count() > 0 and campo_patrimonio.input_value().strip():
            campo_data = linha.locator("input[name^='dtHistorico-']")
            if campo_data.is_visible() and campo_data.is_enabled():
                campo_data.clear()
                campo_data.type(data, delay=50)

    logger.info("Bem selecionado para a UL '{}'.", ul["sigla"])
    return True