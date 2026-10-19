from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global

def consultar_definicao_tipos_observacoes(page: Page, nome: str = "OBSERVAÇÃO TESTE"):
    logger.info("Consultando Definição dos Tipos de Observações com o nome '{}'.", nome)

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    # Preenche Nome do Tipo de Observação
    logger.info("Preenchendo nome do tipo de observação: '{}'.", nome)
    ctx.locator("input[name='model-1']").fill(nome)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    # Seleciona Observação
    linha = ctx.locator("table[name='paginationTable'] tbody tr").filter(
        has=ctx.locator("td").nth(1).filter(
            has_text=nome
        )
    ).first

    if linha.count() == 0:
        logger.info("Nenhuma observação encontrada para '{}'.", nome)
        return False

    logger.info("Observação '{}' encontrada.", nome)

    linha.locator("button[name='submitUse']").click()

    logger.info("Definição de Tipos de Observação com o nome '{}' consultada com sucesso.", nome)

    return True