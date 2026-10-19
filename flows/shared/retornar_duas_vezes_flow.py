from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def retornar_duas_vezes(page: Page) -> None:
    ctx = escopo(page)

    ctx.locator("button[name='submitBack']").click()
    aguardar_ajax_global(page)

    ctx.locator("button[name='submitBack']").click()
    aguardar_ajax_global(page)
