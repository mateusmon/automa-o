from loguru import logger
from playwright.sync_api import Page

from navigation.navegar_para_fornecedor import acessar_fornecedor
from utils.espera import aguardar_ajax_global
from utils.versao_gen import escopo, get_versao


def fornecedor_existe(page: Page, cnpj: str) -> bool:
    """
    Returns True if exact fornecedor exists in search results, False otherwise.
    """

    # Navigation
    acessar_fornecedor(page)

    ctx = escopo(page)

    cnpj_formatado = _format_cnpj(cnpj)

    # Open consultation
    ctx.get_by_role("button", name="Consulta", exact=True).click()
    aguardar_ajax_global(page)

    # Search
    ctx.locator("input[name='model-2']").fill(cnpj_formatado)
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
        cnpj_alvo = cnpj_formatado.strip().lower()
        linhas = ctx.locator("table[name='paginationTable'] tbody tr, table tbody tr").all()

        for linha in linhas:
            celulas = [td.inner_text().strip().lower() for td in linha.locator("td").all()]

            if cnpj_alvo in celulas:
                existe = True
                break

    ctx.get_by_role("button", name="Cancelar").click()
    aguardar_ajax_global(page)

    return existe


def _format_cnpj(cnpj: str) -> str:
    if not cnpj.isdigit() or len(cnpj) != 14:
        raise ValueError(f"CNPJ inválido para formatação: {cnpj}")
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
