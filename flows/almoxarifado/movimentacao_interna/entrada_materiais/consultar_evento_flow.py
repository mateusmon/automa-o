from datetime import datetime

from loguru import logger
from playwright.sync_api import Page

from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao
from utils.versao import escopo
from utils.waits import clicar_com_ajax


def consultar_evento(page: Page, nome: str) -> bool:
    logger.info("Consultando evento '{}'.", nome)

    data_hoje = datetime.now()

    ctx = escopo(page)

    clicar_com_ajax(ctx, "button[name='submitSearch']")

    campo_descricao = ctx.locator(
        "input[name='dsPrevisaoCons']"
    ).or_(ctx.locator("input[name='model-3']"))

    logger.info("Preenchendo descrição com '{}'.", nome)
    campo_descricao.fill(nome)

    clicar_com_ajax(ctx, "button[name='submitSearch']")

    ha_evento = selecionar_movimentacao(ctx, nome)

    if not ha_evento:
        logger.info("Evento '{}' não encontrado.", nome)
        return False

    campo_data_final = ctx.locator("input[name='dtFinal']")
    data_final = datetime.strptime(campo_data_final.input_value(), "%d/%m/%Y")

    if data_final.date() < data_hoje.date():
        logger.info("Evento '{}' está vencido. Atualizando data final para '{}'.", nome, data_hoje.strftime("%d/%m/%Y"))
        campo_data_final.fill(data_hoje.strftime("%d/%m/%Y"))
        clicar_com_ajax(ctx, "button[name='submitFinish']")

    logger.info("Evento consultado.")
    return True