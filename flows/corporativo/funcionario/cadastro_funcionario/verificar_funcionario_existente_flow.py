from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def verificar_funcionario_existente(page: Page, cpf_formatado: str) -> bool:
    """
    Confirma se o Funcionário aparece nos resultados da consulta atual, comparando o
    CPF (texto exato, stripado e em minúsculas) contra as células da grid — mesma regra
    de existência do service legado (`funcionario_existe`). Cancela a consulta ao final,
    achando ou não o registro (mesmo comportamento do legado), deixando a tela pronta
    pra próxima ação (próxima consulta ou criação).
    """
    ctx = escopo(page)

    span_resultado = ctx.locator("span[name='searchResultSize']")
    span_resultado.wait_for(state="visible")
    count = int(span_resultado.inner_text().strip())

    existe = False

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
