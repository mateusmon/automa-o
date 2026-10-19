from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import preencher_campo


def preencher_caracteristicas(page: Page, caracteristica: str = "MARCA AUTOMATIZADA", conteudo: str = "DELL") -> bool:
    logger.info("Preenchendo características.")

    ctx = escopo(page)

    try:
        logger.info("Preenchendo característica '{}'.", caracteristica)
        preencher_campo(ctx, "input[name='cdCaracteristica']", caracteristica)
    except Exception:
        logger.info("Nenhuma característica '{}' encontrada. Rode o teste de definição de características primeiro.", caracteristica)
        return False

    logger.info("Preenchimento de características finalizado.")
    return True
