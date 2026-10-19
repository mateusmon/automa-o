from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def verificar_associacao_ua_existente(page: Page) -> bool:
    """
    Confirma se o Funcionário da consulta atual (já filtrada por CPF) está associado
    a uma U.A. — mesma regra do service legado (`associacao_existe`):

    - sem resultados: cancela a consulta e retorna False;
    - com resultado: abre o registro (`submitUse`) e retorna True somente se o campo
      U.A. (`cdUa`) estiver preenchido e contiver "AUTOMAÇÃO".

    Quando há resultado o registro permanece aberto; a próxima ação
    deve navegar novamente para a página.
    """
    ctx = escopo(page)

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