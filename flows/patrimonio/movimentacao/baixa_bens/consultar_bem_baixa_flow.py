from datetime import datetime
import re

from dateutil.relativedelta import relativedelta
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_patrimonio
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, clicar_com_ajax, preencher_campo


def consultar_bem_baixa(
    page: Page, ug: dict[str, str], material: dict[str, str]
) -> str | bool:
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

    ctx = escopo(page)

    aguardar_ajax_global(page)

    preencher_campo(ctx, "input[name='model-3']", ug["codigo"])
    aguardar_ajax_global(page)

    preencher_campo(ctx, "input[name='model-15']", nome_material)
    aguardar_ajax_global(page)

    hoje_str = obter_data_patrimonio(page, "DD/MM/YYYY")
    campos_data = ctx.locator("tr").filter(has_text=re.compile(r"data\s+(?:de\s+)?aquisi[cç][aã]o", re.IGNORECASE)).locator("input")
    if campos_data.nth(0).is_visible():
        data_hoje = datetime.strptime(hoje_str, "%d/%m/%Y")
        data_inicio = (data_hoje - relativedelta(months=2)).strftime("%d/%m/%Y")

        campos_data.nth(0).fill(data_inicio)
        campos_data.nth(1).dblclick()
        campos_data.nth(1).fill(hoje_str)
        aguardar_ajax_global(page)
        
    clicar_com_ajax(ctx, ctx.locator("button[name='submitSearch']"))

    ctx = escopo(page)

    pagina_consulta_geral_visualizacao = ctx.get_by_role(
        "heading", name="Dados do Bem"
    ).is_visible()

    if pagina_consulta_geral_visualizacao:
        ctx.locator("button[name='submitBack']").click()
        aguardar_ajax_global(page)

        numero_patrimonio = selecionar_num_patrimonial(page, material)

        return numero_patrimonio

    pagina_bem_resultado_consulta = ctx.get_by_text(
        "Total de itens consultados:"
    ).is_visible()

    numero_patrimonio = False

    if pagina_bem_resultado_consulta:
        numero_patrimonio = selecionar_de_consulta_geral(page, material)

    return numero_patrimonio


def selecionar_de_consulta_geral(page: Page, material: dict[str, str]) -> str | bool:
    nome_material = material["nome"]

    ctx = escopo(page)

    # Cada um dos <li> de botões
    li = ctx.locator("div.pagination ul li")

    if li.last.is_enabled():
        li.last.click()
        aguardar_ajax_global(page)

    # <li> de páginas
    li_paginas = ctx.locator("ul[name='paginationSection'] li")

    # Se não houver <li>, não há resultados
    if not li_paginas.first.is_visible():
        return False

    li_paginas.last.click()
    aguardar_ajax_global(page)

    # Escolhendo o último item que contenha o material
    rows = ctx.locator("table.tabela").first.locator("tbody tr")

    row = rows.filter(has_text=nome_material)

    if row.count() == 0:
        return False

    num_patrim = row.last.locator("td[columnid='3']").inner_text()
    row.last.locator("button[name='submitUse']").click()
    aguardar_ajax_global(page)
    return num_patrim


def selecionar_num_patrimonial(page: Page, material: dict[str, str]) -> str | bool:
    nome_material = material["nome"]

    ctx = escopo(page)

    rows = ctx.locator("table.tabela").first.locator("tbody tr")

    row = rows.filter(has_text=nome_material)

    if row.count() == 0:
        return False

    num_patrim = row.last.locator("td[columnid='3']").inner_text()
    row.last.locator("button[name='submitUse']").click()
    aguardar_ajax_global(page)
    return num_patrim
