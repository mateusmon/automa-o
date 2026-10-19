from loguru import logger
from playwright.sync_api import Page

from navigation.navegar_para_unidade_medida import acessar_unidade_medida
from utils.espera import aguardar_ajax_global
from utils.versao_gen import escopo, get_versao


def um_existe(page: Page, sigla_um: str) -> bool:
    """
    Returns True if exact Unidade de Medida exists in search results, False otherwise.
    """

    # Navigation
    acessar_unidade_medida(page)

    ctx = escopo(page)

    # Open consultation
    ctx.get_by_role("button", name="Consulta", exact=True).click()
    aguardar_ajax_global(page)

    # Search
    ctx.locator("input[name='model-2']").fill(sigla_um)
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

    existe = False

    # Ler a tabela e comparar o texto exato
    if count > 0:
        sigla_alvo = sigla_um.strip().lower()
        linhas = ctx.locator("table[name='paginationTable'] tbody tr, table tbody tr").all()

        for linha in linhas:
            celulas = [td.inner_text().strip().lower() for td in linha.locator("td").all()]

            if sigla_alvo in celulas:
                existe = True
                break

    ctx.get_by_role("button", name="Cancelar").click()
    aguardar_ajax_global(page)

    return existe
