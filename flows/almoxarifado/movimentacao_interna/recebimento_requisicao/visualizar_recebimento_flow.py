from playwright.sync_api import Page

from utils.waits import aguardar_ajax_global
from utils.versao import escopo


def visualizar_recebimento(page: Page) -> None:
    # Clicando no botão de visualização da primeira linha
    escopo(page).locator("table.tabela tbody tr").first.locator("button[name^='view-cdRequisicao']").click()
    aguardar_ajax_global(page)
