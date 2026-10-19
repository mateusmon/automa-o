from playwright.sync_api import Page, expect

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_bem(page: Page, ug: dict[str, str], material: dict[str, str]) -> str | bool:
    """
    Flow utilitário. Consulta um bem na página de Consulta Geral de Bens e
    retorna o número do patrimônio correspondente ao material informado.

    Este flow é chamado por um flow de seleção de materiais (bens) quando é necessário
    obter o número patrimonial de um bem. O fluxo típico de uso é:

    1. O flow principal (seleção de materiais) está na aba "Itens" de um
       formulário e aciona a pesquisa de bens clicando no botão de lookup
       do campo de patrimônio.
    2. O sistema abre a página de Consulta Geral de Bens — este flow assume
       o controle a partir deste ponto.
    3. Preenche os campos de UG e material, executa a pesquisa e navega até
       a última página de resultados.
    4. Localiza a última ocorrência do material na tabela e extrai o número
       do patrimônio.
    5. Retorna o número do patrimônio para o flow principal.
    6. O flow principal é responsável por voltar à aba "Itens" e preencher
       o campo com o número retornado.

    Args:
        page: Objeto da página do Playwright.
        ug: Dicionário da unidade gestora. Deve conter a chave "sigla".
        material: Dicionário do material (bem). Deve conter as chaves "nome" e "complemento".

    Returns:
        O número do patrimônio como string, ou False se nenhum bem for encontrado.
    """

    nome_material = material["nome"]
    complemento_material = material["complemento"]
    nome_completo_material = f"{nome_material} {complemento_material}"

    ctx = escopo(page)

    expect(
        ctx.get_by_role("heading", name="Consulta Geral de Bens").or_(ctx.get_by_role("heading", name="Consultar Bem"))
    ).to_be_visible()

    ctx.locator("input[name='model-3']").fill(ug["codigo"])
    ctx.locator("button[name='lookup-model-3']").click()
    aguardar_ajax_global(page)

    ctx.locator("input[name='model-10']").fill(nome_completo_material)
    ctx.locator("button[name='lookup-model-10']").click()
    aguardar_ajax_global(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    pagina_consulta_geral_visualizacao = ctx.get_by_role("heading", name="Consulta geral - Visualização").is_visible()

    if pagina_consulta_geral_visualizacao:
        ctx.locator("button[name='submitBack']").click()
        aguardar_ajax_global(page)

        return selecionar_num_patrimonial(page, material)

    pagina_consulta_geral_visivel = ctx.get_by_role("heading", name="Consulta Geral de Bens -").is_visible()
    pagina_bem_resultado_consulta = ctx.get_by_text("Bem - Resultado da Consulta").is_visible()

    numero_patrimonio = False

    if pagina_consulta_geral_visivel or pagina_bem_resultado_consulta:
        numero_patrimonio = selecionar_de_consulta_geral(page, material)

    return numero_patrimonio


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

    if not li_paginas.is_visible():
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


def selecionar_num_patrimonial(page: Page, material: dict[str, str]) -> str:
    nome_material = material["nome"]
    complemento_material = material["complemento"]
    nome_completo_material = f"{nome_material} {complemento_material}"

    ctx = escopo(page)

    rows = ctx.locator("table.tabela").first.locator("tbody tr")
    row = rows.filter(has_text=nome_completo_material)

    if row.count() == 0:
        return False

    num_patrim = row.last.locator("td[columnid='3']").inner_text()
    row.last.locator("button[name='submitUse']").click()
    aguardar_ajax_global(page)
    return num_patrim
