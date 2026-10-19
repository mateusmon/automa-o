from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo

from utils.competencia_financeira import obter_data_almoxarifado


def preencher_data_transferencia(page: Page) -> None:
    data_hoje = obter_data_almoxarifado(page, "DD/MM/YYYY")

    logger.info("Iniciou preenchimento da Data da transferencia '{}'.", data_hoje)

    ctx = escopo(page)
    campo = ctx.locator("input[name='dtRequisicao']")
    campo.click()
    campo.fill(data_hoje)

    logger.info("Finalizou preenchimento da Data da transferencia '{}'.", data_hoje)