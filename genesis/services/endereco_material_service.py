from loguru import logger
from playwright.sync_api import Page

from navigation.navegar_para_endereco_material import acessar_endereco_material
from utils.espera import aguardar_ajax_global
from utils.versao_gen import escopo, get_versao


def endereco_existe(page: Page, descricao_endereco: str, sigla_almoxarifado: str) -> bool:
    """
    Returns True if exact endereco_material exists in search results, False otherwise.
    """
    # Navigation
    if not acessar_endereco_material(page):
        logger.warning("Menu 'Endereço de Estoque' não disponível para este cliente. Ignorando verificação de endereço.")
        return False

    ctx = escopo(page)

    # Open consultation
    ctx.get_by_role("button", name="Consulta", exact=True).click()
    aguardar_ajax_global(page)

    # Search
    ctx.locator("input[name='model-1']").fill(sigla_almoxarifado)
    ctx.locator("button[name='lookup-model-1']").click()
    aguardar_ajax_global(page)

    ctx.locator("input[name='model-3']").fill(descricao_endereco)
    ctx.get_by_title("Consultar novo registro").click()
    aguardar_ajax_global(page)

    if get_versao() >= 4:
        # Esse span apresenta o total de itens consultados
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

    raise RuntimeError(f"Multiple endereco_material detected. Count: {count}")
