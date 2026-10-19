from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def confirmar_movimentacao(page: Page) -> None:
    "Flow que somente confirma a movimentação e espera pela página de sucesso."

    ctx = escopo(page)

    botao_confirmar = ctx.locator("button[name='submitConfirm']").last
    botao_finalizar = ctx.locator("button[name='submitFinish']").last
    
    btn = (botao_confirmar.or_(botao_finalizar))

    btn.click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)
