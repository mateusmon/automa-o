from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def voltar_para_resultados_consulta(page: Page) -> None:

    ctx = escopo(page)

    ctx.get_by_role("button", name="Retornar").click()
    aguardar_ajax_global(page)

    # Clicando no botão de imprimir o último item adicionado
    ctx.locator('button[name="submitPrint-1-7"]').click()
    aguardar_ajax_global(page)
