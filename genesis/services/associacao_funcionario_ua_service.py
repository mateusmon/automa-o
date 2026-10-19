from playwright.sync_api import Page

from navigation.navegar_para_funcionario import acessar_funcionario
from utils.espera import aguardar_ajax_global
from utils.versao_gen import escopo


def associacao_existe(page: Page, matricula: str) -> bool:
    """
    Returns True if there's an association between UA and 
    funcionario.

    Raises if duplicates detected.
    """

    # Navigation
    if not acessar_funcionario(page):
        return False

    ctx = escopo(page)

    # Open consultation
    ctx.get_by_role("button", name="Consulta", exact=True).click()
    aguardar_ajax_global(page)

    # Search
    campo_cpf = ctx.locator("#model-4")
    campo_cpf.clear()
    campo_cpf.fill(_format_cpf(matricula))

    ctx.get_by_title("Consultar novo registro").click()
    aguardar_ajax_global(page)

    ctx.wait_for_selector("table[name='paginationTable']")

    span_resultado = ctx.locator("span[name='searchResultSize']")
    span_resultado.wait_for(state="visible")
    count = int(span_resultado.inner_text().strip())

    if count == 0:
        ctx.get_by_role("button", name="Cancelar").click()
        aguardar_ajax_global(page)
        return False

    ctx.locator("button[name='submitUse']").click()
    aguardar_ajax_global(page)

    value = ctx.locator("input[name='cdUa']").input_value()
    if not value or "AUTOMAÇÃO" not in value:
        return False

    return True


def _format_cpf(cpf: str) -> str:
    if not cpf.isdigit() or len(cpf) != 11:
        raise ValueError(f"CPF inválido para formatação: {cpf}")

    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
