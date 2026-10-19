from playwright.sync_api import Page

from navigation.navegar_para_ua import acessar_ua
from utils.espera import aguardar_ajax_global
from utils.versao_gen import escopo, get_versao


def ua_existe(page: Page, sigla: str) -> bool:
    """
    Returns True if exact UA exists in search results, False otherwise.
    Raises if duplicates detected.
    """
    if not acessar_ua(page):
        return False

    ctx = escopo(page)

    # Open consultation
    ctx.get_by_role("button", name="Consulta", exact=True).click()
    aguardar_ajax_global(page)

    # Search
    ctx.locator("input[name='model-4']").fill(sigla)
    ctx.get_by_title("Consultar novo registro").click()
    aguardar_ajax_global(page)

    if get_versao() >= 4:
        span_resultado = ctx.locator("span[name='searchResultSize']")
        span_resultado.wait_for(state="visible")
        count = int(span_resultado.inner_text().strip())
    else:
        ctx.wait_for_selector("table[name='paginationTable']", timeout=10_000)
        linhas = ctx.locator("table[name='paginationTable'] tbody.scrollBody tr")
        count = linhas.count()

    ctx.get_by_role("button", name="Cancelar").click()
    aguardar_ajax_global(page)

    if count == 0:
        return False

    if count == 1:
        return True

    raise RuntimeError(f"Multiple UAs detected. Count: {count}")
