from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def alterar_pedido_ressuprimento(page: Page) -> None:
    logger.info("Iniciou alteração do pedido de ressuprimento.")

    ctx = escopo(page)

    campo_manual = ctx.locator("input[name='inManual'][value='S']")
    campo_automatico = ctx.locator("input[name='inManual'][value='N']")

    if campo_automatico.is_checked():
        logger.info("Alterando pedido de ressuprimento: 'automático' -> 'manual'.")
        campo_manual.click()
    else:
        logger.info("Alterando pedido de ressuprimento: 'manual' -> 'automático'.")
        campo_automatico.click()

    aguardar_ajax_global(page)

    page.once("dialog", _aceitar_confirmacao)
    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou alteração do pedido de ressuprimento.")


def _aceitar_confirmacao(dialog) -> None:
    logger.info("Caixa de diálogo capturada: {}", dialog.message)
    dialog.accept()
    logger.info("Diálogo aceito.")