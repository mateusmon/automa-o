from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import preencher_campo


def preencher_materiais(page: Page, bem: dict[str, str]) -> None:
    logger.info("Iniciou preenchimento de materiais do Catálogo de Materiais.")

    ctx = escopo(page)

    logger.info("Preenchendo nome do bem: '{}'.", f"{bem['nome']} {bem['complemento']}")
    preencher_campo(ctx, "input[name='bemServOrgao-1-3']", f"{bem['nome']} {bem['complemento']}",)

    logger.info("Finalizou preenchimento de materiais do Catálogo de Materiais.")
