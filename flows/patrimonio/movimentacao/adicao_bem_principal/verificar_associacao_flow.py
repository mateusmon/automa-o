from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo


def verificar_associacao(page: Page) -> bool:
    logger.info("Iniciou verificação de associação entre bens.")

    ctx = escopo(page)

    input_primeiro_bem_adicionado = ctx.locator("input[name='cdBemPerm-1-3']")

    if input_primeiro_bem_adicionado.is_enabled():
        logger.info("Não há bens associados ao bem principal.")
        logger.info("Pulando teste.")
        return False
    
    logger.info("Finalizou verificação de associação entre bens.")
    return True
