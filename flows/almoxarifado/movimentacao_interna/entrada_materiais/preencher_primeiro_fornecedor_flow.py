from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import preencher_campo


def preencher_primeiro_fornecedor(page: Page) -> None:
    """
    Preenche o campo Fornecedor (agente de entrada) selecionando o PRIMEIRO
    fornecedor disponível na listagem.

    Alguns tipos de entrada não aceitam o fornecedor padrão do blueprint. Ao
    passar "   " (três espaços) para o `preencher_campo`, o lookup abre a
    listagem completa e o primeiro resultado é selecionado automaticamente.

    Parâmetros:
        page (Page): Instância da página do Playwright.
    """
    logger.info("Iniciou preenchimento do primeiro fornecedor disponível.")

    ctx = escopo(page)
    logger.info("Preenchendo campo Fornecedor com três espaços para selecionar o primeiro fornecedor disponível.")
    preencher_campo(ctx, "#agenteEntrada", "   ")

    logger.info("Finalizou preenchimento do primeiro fornecedor disponível.")
