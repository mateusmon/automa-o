from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def confirmar_transferencia_externa(page: Page) -> None:
    ctx = escopo(page)
    ctx.locator("button[name='submitFinish']").last.click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)
