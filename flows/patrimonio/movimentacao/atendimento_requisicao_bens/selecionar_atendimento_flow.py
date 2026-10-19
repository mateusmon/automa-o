from playwright.sync_api import Page
from loguru import logger

from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao


def selecionar_atendimento(page: Page, ul: dict[str, str]) -> bool:
    logger.info("Iniciou seleção de atendimento de requisição de bens para a UL '{}'.", ul["sigla"])

    ha_atendimentos = selecionar_movimentacao(page, ul["sigla"])

    if not ha_atendimentos:
        logger.info("Nenhum atendimento encontrado para '{}'.", ul["sigla"])
        return False

    logger.info("Finalizou seleção de atendimento de requisição de bens para a UL '{}'.", ul["sigla"])
    return True
