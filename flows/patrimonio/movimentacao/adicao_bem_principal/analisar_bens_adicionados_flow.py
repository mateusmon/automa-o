from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo


def analisar_bens_adicionados(page: Page) -> bool:
    logger.info("Iniciou análise de bens .")

    ctx = escopo(page)

    input_desabilitado = ctx.locator("input[name='cdBemPerm-1-3']").is_disabled()
    
    if input_desabilitado:
        logger.info("Há um bem associado.")
        logger.info("Finalizou análise seleção de bens.")
        return True
    
    logger.info("Não há bens adicionados.")
    return False
