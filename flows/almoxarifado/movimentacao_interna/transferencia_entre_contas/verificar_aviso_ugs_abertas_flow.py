from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo


def verificar_aviso_ugs_abertas(page: Page) -> bool:
    logger.info("Iniciou verificação de aviso de UGs abertas.")

    ctx = escopo(page)
    alerta = ctx.locator(".alert-danger")
    if alerta.is_visible():
        logger.info("Todas as UGs devem estar com o mesmo Ano/Mês aberto para fazer a transferência.")
        return False
    
    logger.info("Não há aviso de UGs abertas.")
    logger.info("Finalizou verificação de aviso de UGs abertas.")
    return True
