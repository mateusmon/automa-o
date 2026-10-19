from playwright.sync_api import Page

from navigation.navegar_para_usuario import acessar_usuario
from utils.espera import aguardar_ajax_global
from utils.versao_gen import escopo


def usuario_existe(page: Page, nome_funcionario: str) -> bool:
    """
    Returns True if exact usuario exists in search results, False otherwise.
    """

    # Navigation
    if not acessar_usuario(page):
        return False

    ctx = escopo(page)

    # Open consultation
    ctx.get_by_role("button", name="Consulta", exact=True).click()
    aguardar_ajax_global(page)

    # Search
    ctx.locator("input[name='model-1']").fill(nome_funcionario)
    ctx.locator("button[name='lookup-model-1']").click()
    aguardar_ajax_global(page)

    if ctx.locator("div[name='divWarningMsg']").is_visible():
        return False

    ctx.get_by_title("Consultar novo registro").click()
    aguardar_ajax_global(page)

    # Verificar quantidade de resultados
    span_resultado = ctx.locator("span[name='searchResultSize']")
    span_resultado.wait_for(state="visible")
    count = int(span_resultado.inner_text().strip())

    existe = False

    if count > 0:
        nome_alvo = nome_funcionario.strip().lower()
        linhas = ctx.locator("table tbody tr").all()

        for linha in linhas:
            celulas = [td.inner_text().strip().lower() for td in linha.locator("td").all()]

            for celula in celulas:
                nome_sem_prefixo = celula.split(" - ", 1)[-1].strip()
                if nome_sem_prefixo == nome_alvo:
                    existe = True
                    break

            if existe:
                break

    ctx.get_by_role("button", name="Cancelar").click()
    aguardar_ajax_global(page)

    return existe
