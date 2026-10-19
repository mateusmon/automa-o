from playwright.sync_api import Page
from loguru import logger

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, proximo_nome


def alterar_selecao_bens(page: Page) -> None:
    logger.info("Iniciou alteração de última seleção de bens.")
 
    ctx = escopo(page)

    campo = ctx.locator("input[name='dsObjetivo']")
    logger.info("Alterando o campo de objetivo da seleção de bens. Valor atual: '{}'.", campo.input_value())
    campo.fill(proximo_nome(campo.input_value()))
    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)

    ctx.get_by_role("button", name="Retornar").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou alteração de última de seleção de bens.")
