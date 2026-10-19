from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global
from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao


def selecionar_transferencia(page: Page, funcionario: dict[str, str]) -> bool:
    logger.info("Iniciou seleção de transferência de detentor do bem para '{}'.", funcionario["nome"])

    ctx = escopo(page)
    encontrou = selecionar_movimentacao(ctx, funcionario["nome"])

    if not encontrou:
        logger.info("Nenhuma transferência de detentor do bem encontrada para '{}'.", funcionario["nome"])
        return False

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou seleção de transferência de detentor do bem para '{}'.", funcionario["nome"])
    return True
