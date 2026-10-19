from playwright.sync_api import Page

from utils.versao import escopo, get_versao
from utils.waits import aguardar_ajax_global


def verificar_ua_existente(page: Page) -> bool:
    """
    Confirma se a UA existe nos resultados da consulta atual (já filtrada por Sigla),
    pela mesma regra do service legado (`ua_existe`): decide pela quantidade de
    resultados, não por texto. 0 = ausente, 1 = existente, mais de 1 = duplicidade.
    Cancela a consulta antes de decidir, deixando a tela pronta pra próxima ação.

    :raises RuntimeError: Se mais de uma UA for encontrada.
    """
    ctx = escopo(page)

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
