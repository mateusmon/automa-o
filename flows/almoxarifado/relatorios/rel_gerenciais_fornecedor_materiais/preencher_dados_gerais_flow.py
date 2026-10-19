from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import preencher_campo


def preencher_dados_gerais(page: Page, fornecedor: dict[str, str]) -> None:
    logger.info(
        "Iniciou preenchimento de dados gerais para o fornecedor '{}'.",
        fornecedor["nome"],
    )

    ctx = escopo(page)

    logger.info("Preenchendo nome do fornecedor: '{}'.", fornecedor["nome"])
    preencher_campo(ctx, "input[name='fornecedor']", fornecedor["nome"])

    logger.info(
        "Finalizou preenchimento de dados gerais para o fornecedor '{}'.",
        fornecedor["nome"],
    )
