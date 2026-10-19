from playwright.sync_api import Page

from navigation.navegar_para_instalacao import acessar_instalacao
from utils.espera import aguardar_ajax_global
from utils.versao_gen import escopo


def instalacao_existe(page: Page, nome: str) -> bool:
    """
    Returns True if exact instalacao exists in search results, False otherwise.
    """

    # Navigation
    if not acessar_instalacao(page):
        return False

    ctx = escopo(page)

    # Search
    ctx.get_by_role("button", name="Consulta", exact=True).click()
    aguardar_ajax_global(page)

    ctx.locator("input[name='model-2']").fill(nome)
    ctx.get_by_title("Consultar novo registro").click()
    aguardar_ajax_global(page)

    # Verificar quantidade de resultados
    span_resultado = ctx.locator("span[name='searchResultSize']")
    span_resultado.wait_for(state="visible")
    count = int(span_resultado.inner_text().strip())

    existe = False

    # Ler a tabela e comparar o texto exato
    if count > 0:
        nome_alvo = nome.strip().lower()
        linhas = ctx.locator("table tbody tr").all()

        for linha in linhas:
            celulas = [td.inner_text().strip().lower() for td in linha.locator("td").all()]

            if nome_alvo in celulas:
                existe = True
                break

    ctx.get_by_role("button", name="Cancelar").click()
    aguardar_ajax_global(page)

    return existe