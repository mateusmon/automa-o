from typing import Literal
from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import preencher_campo, select_tipo


def preencher_dados_gerais(
    page: Page, 
    ug: dict[str, str], 
    tipo_bem: Literal[
        "PRÓPRIO CONTROLADO", 
        "DE TERCEIROS", 
        "PRÓPRIO CONTABILIZADO"
    ] = "PRÓPRIO CONTABILIZADO"
) -> None:

    logger.info("Iniciou o preenchimento dos dados gerais para o tipo '{}'.", tipo_bem )

    ctx = escopo(page)

    ug_locator = ctx.locator('input[name="ug"]')
    ug_locator.wait_for(state="visible")

    valor_atual = ug_locator.input_value()

    if ug["nome"] not in valor_atual:
        preencher_campo(ctx, 'input[name="ug"]', ug["codigo"])
    
    select_tipo(ctx, "tipoBem", tipo_bem)
    
    logger.info("Finalizou o preenchimento dos dados gerais para o tipo '{}'.", tipo_bem)
