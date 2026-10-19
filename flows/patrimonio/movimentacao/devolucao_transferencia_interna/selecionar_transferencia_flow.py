from playwright.sync_api import Page
from loguru import logger

from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao


def selecionar_transferencia(page: Page, ul: dict[str, str]) -> bool:
    logger.info("Iniciou seleção de transferência interna para a UL '{}'.", ul["sigla"])

    ha_transferencias = selecionar_movimentacao(page, ul["sigla"], "tbody.scrollBody tr")

    if not ha_transferencias:
        logger.info("Nenhuma transferência interna encontrada para a UL '{}'.", ul["sigla"])
        return False

    logger.info("Finalizou seleção de transferência interna para a UL '{}'.", ul["sigla"])
    return True
