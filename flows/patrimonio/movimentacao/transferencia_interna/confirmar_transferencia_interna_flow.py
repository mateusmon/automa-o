from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def confirmar_transferencia_interna(page: Page) -> bool:

    ctx = escopo(page)

    ctx.locator("button[name='submitConfirm']").last.click()
    aguardar_ajax_global(page)

    # Verifica se o sistema exibiu uma mensagem de erro para o patrimônio informado.
    # Quando isso acontece, obtém a mensagem presente no atributo "title" do campo,
    # registra o motivo no log e orienta que é necessário realizar primeiro o
    # recebimento da Transferência Interna desse patrimônio antes de tentar uma nova transferência.
    if ctx.locator("div[name='divErrorMsg']").is_visible():
        mensagem_erro = ctx.locator("input[name='cdBemPerm-2-3']").get_attribute("title")

        if mensagem_erro:
            numero_patrimonio = ctx.locator("input[name='cdBemPerm-2-3']").inner_text()

            logger.warning(mensagem_erro)
            logger.warning("Faça primeiro o recebimento da Transferência Interna do Patrimônio {} para, em seguida, realizar a transferência interna.", numero_patrimonio)

        return False

    ctx.locator("button[name='finish']").last.click()
    aguardar_ajax_global(page)
    return True
