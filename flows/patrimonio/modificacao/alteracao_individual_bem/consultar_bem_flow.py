from playwright.sync_api import Page, expect

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_bem(page: Page, ug: dict[str, str], material: dict[str, str]) -> str | bool:
    """
    Flow utilitário. Consulta um bem na página de Consulta Geral de Bens
    e seleciona o último bem da tabela de resultados.
    """
    nome_completo_material = f"{material['nome']} {material['complemento']}"

    ctx = escopo(page)

    # Garantindo que se está na tabela correta
    tabela = ctx.locator("table[name='paginationTable']")
    expect(tabela).to_contain_text("Identificação")
    expect(tabela).to_contain_text("Conteúdo")
    expect(tabela).to_contain_text("Exceção")

    # Localiza apenas as linhas que contêm o texto "UG"
    linhas_ug = ctx.locator("table[name='paginationTable'] tbody tr").filter(has_text="UG")

    # Executa as ações em lote para todas as linhas filtradas
    for linha in linhas_ug.all():
        linha.locator("input[type='text']").fill(ug["codigo"])
        linha.locator("button").click()
        aguardar_ajax_global(page)

    linha_material = ctx.locator("tr").filter(has_text="Material:")
    linha_material.locator("input[type='text']").fill(nome_completo_material)
    linha_material.locator("button").click()
    aguardar_ajax_global(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    return selecionar_de_consulta_geral(page, material)


def selecionar_de_consulta_geral(page: Page, material: dict[str, str]) -> str | bool:
    nome_material = material["nome"]
    complemento_material = material["complemento"]
    nome_completo_material = f"{nome_material} {complemento_material}"

    ctx = escopo(page)

    li = ctx.locator("div.pagination ul li")

    if li.last.is_enabled():
        li.last.click()
        aguardar_ajax_global(page)

    li_paginas = ctx.locator("ul[name='paginationSection'] li")

    if li_paginas.count() == 0:
        return False

    li_paginas.last.click()
    aguardar_ajax_global(page)

    rows = ctx.locator("table.tabela").first.locator("tbody tr")
    row = rows.filter(has_text=nome_completo_material)

    if row.count() == 0:
        return False

    num_patrim = row.last.locator("td[columnid='3']").inner_text()
    row.last.locator("button[name='submitUse']").click()
    aguardar_ajax_global(page)
    return num_patrim
