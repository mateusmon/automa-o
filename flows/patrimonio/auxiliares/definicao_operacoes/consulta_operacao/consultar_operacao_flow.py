from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, preencher_campo

def consultar_operacao(page: Page, operacao: str, nome: str):
    logger.info("Consultando Operação {} de tipo {}.", nome, operacao)

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    # Preenche Tipo de Operação
    logger.info("Preenchendo tipo de operação: '{}'.", operacao)
    preencher_campo(ctx, "input[name='model-0']", operacao)

    #Preenche Nome da Forma de Operação
    logger.info("Preenchendo nome da operação: '{}'.", nome)
    ctx.locator("input[name='model-2']").fill(nome)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    # Selecionar Operação
    linha = ctx.locator("table[name='paginationTable'] tbody tr").filter(
        has=ctx.locator("td").nth(2).filter(
            has_text=nome
        )
    ).first

    if linha.count() == 0:
        logger.info("Nenhum operação com o nome '{}' encontrada.", nome)
        return False

    logger.info("Foi encontrada uma operação com o nome '{}' .", nome)
    
    linha.locator("button[name='submitUse']").click()

    logger.info("Operação '{}' de tipo '{}' consultada.", nome, operacao)

    return True