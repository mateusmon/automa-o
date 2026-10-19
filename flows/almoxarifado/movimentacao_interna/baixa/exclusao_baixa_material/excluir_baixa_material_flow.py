from loguru import logger
from playwright.sync_api import Page

from flows.shared.excluir_movimento_flow import excluir_movimento

def excluir_baixa_material(page: Page):
    logger.info("Excluindo baixa de material.")
    
    excluir_movimento(page)

    logger.info("Baixa de material excluido.")