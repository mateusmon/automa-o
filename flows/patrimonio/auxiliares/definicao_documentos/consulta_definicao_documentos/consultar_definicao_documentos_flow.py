from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global

def consultar_definicao_documentos(page: Page, nome: str = "DOCUMENTO TESTE"):
    logger.info("Consultando definição do documento '{}'.", nome)

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    # Preenche Nome do Tipo de Documento
    logger.info("Preenchendo nome do tipo de documento: '{}'.", nome)
    ctx.locator("input[name='model-1']").fill(nome)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    # Selecionar Documento
    linha = ctx.locator("table[name='paginationTable'] tbody tr").filter(
        has=ctx.locator("td").nth(1).filter(
            has_text=nome
        )
    ).first

    if linha.count() == 0:
        logger.info("Nenhum documento com o nome '{}' foi encontrado.", nome)
        return False

    logger.info("Foi encontrado um documento com o nome '{}' .", nome)
    
    linha.locator("button[name='submitUse']").click()
    aguardar_ajax_global(page)

    logger.info("Definição do documento '{}' consultado.", nome)

    return True