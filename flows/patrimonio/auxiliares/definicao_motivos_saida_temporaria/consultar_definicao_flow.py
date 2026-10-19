from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global
from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao


def consultar_definicao(page: Page) -> bool:
    logger.info("Iniciou consulta de motivo.")

    ctx = escopo(page)

    ctx.click("button[name='submitSearch']")
    aguardar_ajax_global(page)

    logger.info("Preenchendo motivo: 'MOTIVO PLAUSÍVEL DE SAÍDA'.")
    ctx.type("input[name='model-1']", "MOTIVO PLAUSÍVEL DE SAÍDA", delay=50)

    ctx.click("button[name='submitSearch']")
    aguardar_ajax_global(page)

    resultado = selecionar_movimentacao(ctx, "MOTIVO PLAUSÍVEL DE SAÍDA")

    if not resultado:
        logger.info("Nenhum resultado encontrado para seleção do motivo 'MOTIVO PLAUSÍVEL DE SAÍDA'.")
        return False

    logger.info("Foi encontrado um resultado para seleção do motivo 'MOTIVO PLAUSÍVEL DE SAÍDA'.")
    logger.info("Finalizou consulta de motivo.")
    return True
