from loguru import logger
from playwright.sync_api import Page

from navigation.navegar_para_almoxarifado import acessar_almoxarifado
from utils.espera import aguardar_ajax_global
from utils.versao_gen import escopo


def almoxarifado_existe(page: Page, sigla: str) -> bool:
    """
    Returns True if exact almoxarifado exists in search results, False otherwise.
    """

    # Navigation
    acessar_almoxarifado(page)

    ctx = escopo(page)

    # Search
    ctx.get_by_role("button", name="Consulta", exact=True).click()
    aguardar_ajax_global(page)

    ctx.locator("input[name='model-4']").fill(sigla)
    ctx.get_by_title("Consultar novo registro").click()
    aguardar_ajax_global(page)

    # Verificar quantidade de resultados
    span_resultado = ctx.locator("span[name='searchResultSize']")
    span_resultado.wait_for(state="visible")
    count = int(span_resultado.inner_text().strip())

    existe = False

    # Ler a tabela e comparar o texto exato
    if count > 0:
        sigla_alvo = sigla.strip().lower()
        linhas = ctx.locator("table tbody tr").all()

        for linha in linhas:
            celulas = [td.inner_text().strip().lower() for td in linha.locator("td").all()]

            if sigla_alvo in celulas:
                existe = True
                break

    ctx.get_by_role("button", name="Cancelar").click()
    aguardar_ajax_global(page)

    return existe