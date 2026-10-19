from loguru import logger
from playwright.sync_api import Page

from navigation.navegar_para_funcionario import acessar_funcionario
from utils.espera import aguardar_ajax_global
from utils.versao_gen import escopo


def funcionario_existe(page: Page, matricula: str) -> bool:
    """
    Returns True if exact funcionario exists in search results, False otherwise.
    """

    # Navigation
    if not acessar_funcionario(page):
        return False

    ctx = escopo(page)

    cpf_formatado = _format_cpf(matricula)

    # Open consultation
    ctx.get_by_role("button", name="Consulta", exact=True).click()
    aguardar_ajax_global(page)

    # Search
    campo_cpf = ctx.locator("input[name='model-4'], #model-4").first
    campo_cpf.clear()
    campo_cpf.fill(cpf_formatado)

    ctx.get_by_title("Consultar novo registro").click()
    aguardar_ajax_global(page)

    # Verificar quantidade de resultados
    span_resultado = ctx.locator("span[name='searchResultSize']")
    span_resultado.wait_for(state="visible")
    count = int(span_resultado.inner_text().strip())

    existe = False

    # Ler a tabela e comparar o texto exato
    if count > 0:
        cpf_alvo = cpf_formatado.strip().lower()
        linhas = ctx.locator("table tbody tr").all()

        for linha in linhas:
            celulas = [td.inner_text().strip().lower() for td in linha.locator("td").all()]

            if cpf_alvo in celulas:
                existe = True
                break

    ctx.get_by_role("button", name="Cancelar").click()
    aguardar_ajax_global(page)

    return existe


def _format_cpf(cpf: str) -> str:
    if not cpf.isdigit() or len(cpf) != 11:
        raise ValueError(f"CPF inválido para formatação: {cpf}")

    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
