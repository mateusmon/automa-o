from loguru import logger
from playwright.sync_api import Page

from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao
from utils.versao import escopo


def selecionar_configuracao_documentacao(page: Page, nome_configuracao: str) -> bool:
    logger.info("Iniciou a seleção de configuração de documentação com o nome '{}'.", nome_configuracao)

    ctx = escopo(page)

    existe_configuracao = selecionar_movimentacao(ctx, nome_configuracao)

    if not existe_configuracao:
        logger.info("Nenhuma configuração encontrada com o nome '{}'.", nome_configuracao)
        return False

    logger.info("Finalizou a seleção de configuração de documentação com o nome '{}'.", nome_configuracao)
    return True
