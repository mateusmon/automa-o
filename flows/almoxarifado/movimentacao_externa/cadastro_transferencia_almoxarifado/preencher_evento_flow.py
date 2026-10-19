from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import preencher_campo


def preencher_evento(page: Page, evento: dict[str, str],) -> None:
    logger.info("Iniciou preenchimento de evento de almoxarifado solicitante '{}'.", evento["nome"])

    ctx = escopo(page)
    logger.info("Preenchendo nome do evento de almoxarifado solicitante: '{}'.", evento["nome"])
    preencher_campo(ctx, "input[name='previsaoCons']", evento["nome"])

    logger.info("Finalizou preenchimento de evento de almoxarifado solicitante '{}'.", evento["nome"])
