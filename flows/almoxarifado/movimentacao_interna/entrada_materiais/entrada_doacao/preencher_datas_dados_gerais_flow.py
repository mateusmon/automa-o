from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_almoxarifado
from utils.versao import escopo


def preencher_datas_dados_gerais(page: Page) -> None:
    logger.info("Iniciou preenchimento de datas na aba de dados gerais.")

    ctx = escopo(page)
    _preencher(ctx, page)


def _preencher(ctx, page: Page) -> None:
    data_hoje = obter_data_almoxarifado(page, formato="DDMMYYYY")

    data_recebimento = ctx.locator('input[name="dtRecebimento"]')
    data_atesto = ctx.locator('input[name="dtContabil"]')

    logger.info("Preenchendo data de recebimento: '{}'.", data_hoje)
    data_recebimento.clear()
    data_recebimento.type(data_hoje, delay=50)

    logger.info("Preenchendo data de atesto: '{}'.", data_hoje)
    data_atesto.clear()
    data_atesto.type(data_hoje, delay=50)

    logger.info("Finalizou preenchimento de datas na aba de dados gerais com a data {}", data_hoje)
