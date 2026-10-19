from playwright.sync_api import Page

from navigation.navegar_para_ul import acessar_ul
from utils.espera import aguardar_ajax_global
from utils.versao_gen import escopo, get_versao


def ul_existe(page: Page, endereco: str) -> bool:
    """
    Returns True if exact UL exists in search results, False otherwise.
    """

    # Navigation
    acessar_ul(page)

    ctx = escopo(page)

    # Open consultation
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    # Search
    ctx.locator("input[name='model-7']").fill(endereco)
    ctx.locator("button[name='lookup-model-7']").click()
    ctx.locator("button[name='submitSearch']").click()
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
        endereco_alvo = endereco.strip().lower()
        linhas = ctx.locator("table[name='paginationTable'] tbody tr, table tbody tr").all()

        for linha in linhas:
            celulas = [td.inner_text().strip().lower() for td in linha.locator("td").all()]

            if any(endereco_alvo in c for c in celulas):
                existe = True
                break

    cancel_btn = ctx.locator("button[name='submitCancel']").or_(ctx.get_by_role("button", name="Cancelar"))
    if cancel_btn.is_visible():
        cancel_btn.click()
        aguardar_ajax_global(page)

    return existe
