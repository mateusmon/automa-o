from typing import Literal
from playwright.sync_api import Page
from loguru import logger

from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao


def selecionar_configuracao(page: Page, nome_configuracao: str, posicao: Literal["first", "last"] = "first") -> bool:
    logger.info("Iniciou a seleção de configuração com o nome '{}'.", nome_configuracao)

    existe_configuracao = selecionar_movimentacao(page, nome_configuracao, posicao=posicao)
    
    if not existe_configuracao:
        logger.info("Nenhuma configuração com o nome '{}' encontrada.", nome_configuracao)
        return False

    logger.info("Finalizou a seleção de configuração com o nome '{}'.", nome_configuracao)
    return True
