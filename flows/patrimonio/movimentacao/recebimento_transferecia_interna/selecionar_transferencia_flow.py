from loguru import logger
from playwright.sync_api import Page

from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao


def selecionar_transferencia(page: Page, ul: dict[str, str]) -> bool:
    endereco_ul = ul["endereco"]

    logger.info("Iniciou seleção da transferência interna. UL: '{}'.", endereco_ul)

    ha_transferencias = selecionar_movimentacao(page, endereco_ul, "tbody.scrollBody tr")

    if not ha_transferencias:
        logger.info("Nenhuma transferência encontrada para a UL de endereço '{}'.", endereco_ul)
        return False

    logger.info("Consulta da transferência interna finalizada. UL: '{}'.", endereco_ul)
    return True
