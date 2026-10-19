from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import clicar_com_ajax


def preencher_observacao(page: Page) -> None:
    logger.info("Iniciou preenchimento de observação.")

    ctx = escopo(page)
    _preencher(ctx, 2)
    _preencher(ctx, 3)
    
    logger.info("Finalizou preenchimento de observação.")

def _preencher(ctx, linha: int) -> None:
    # Corrigido de input para button
    clicar_com_ajax(ctx, "button:text-is('Observações')")
    clicar_com_ajax(ctx, "button[name='submitAddLine']")
    logger.info("Preenchendo observação 'OBSERVACAO AUTOMATIZADA' na linha '{}'.", linha)
    ctx.locator("textarea[name='dsObs']").fill("OBSERVACAO AUTOMATIZADA")
    clicar_com_ajax(ctx, "button[name='submitBack']")
    clicar_com_ajax(ctx, "button[name='submitFinish']")