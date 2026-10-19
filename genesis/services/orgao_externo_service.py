from loguru import logger
from playwright.sync_api import Page

from navigation.navegar_para_orgao_externo import acessar_orgao_externo
from utils.espera import aguardar_ajax_global
from utils.versao_gen import escopo


def orgao_externo_existe(page: Page, nome: str) -> bool:
    """
    Returns True if exact orgao externo exists in search results, False otherwise.
    """

    # Navigation
    acessar_orgao_externo(page)

    ctx = escopo(page)

    # Open consultation
    ctx.get_by_role("button", name="Consulta", exact=True).click()
    aguardar_ajax_global(page)

    ctx.locator("input[name='model-4']").fill(nome)
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    # Esse span apresenta o total de itens consultados    
    span_resultado = ctx.locator("span[name='searchResultSize']")
    span_resultado.wait_for(state="visible")
    count = int(span_resultado.inner_text().strip())

    ctx.get_by_role("button", name="Cancelar").click()
    aguardar_ajax_global(page)

    if count == 0:
        return False

    if count == 1:
        return True

    raise RuntimeError(f"Multiple orgaos externos detected. Count: {count}")