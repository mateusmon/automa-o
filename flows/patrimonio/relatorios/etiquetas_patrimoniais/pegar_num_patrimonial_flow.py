from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, clicar_menu_com_retry, preencher_campo


def pegar_num_patrimonial(page: Page, ug: dict[str, str], material: dict[str, str]) -> str | bool:
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

    ctx = escopo(page)

    nome_material = material["nome"]

    if ctx.locator("input[name='model-3']").is_visible(): 
        preencher_campo(ctx, "input[name='model-3']", ug["codigo"])
        aguardar_ajax_global(page)
    

    preencher_campo(ctx, "input[name='model-15']", nome_material)
    aguardar_ajax_global(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    pagina_consulta_geral_visualizacao = ctx.get_by_role("heading", name="Dados do Bem").is_visible()

    if pagina_consulta_geral_visualizacao:
        ctx.locator("button[name='submitBack']").click()
        aguardar_ajax_global(page)
        numero_patrimonio = selecionar_num_patrimonial(page, material)

        return numero_patrimonio
    
    pagina_consulta_geral_visivel = page.get_by_text("Total de itens consultados:")

    numero_patrimonio = False

    if pagina_consulta_geral_visivel:
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
    
    # <li> de de páginas
    li_paginas = ctx.locator("ul[name='paginationSection'] li").first

    # Se não houver <li>, não há resultados
    if not li_paginas.is_visible():
        return False
    
    li_paginas.last.click()
    aguardar_ajax_global(page)

    # Escolhendo o último item que contenha o material
    rows = ctx.locator("table.tabela").first.locator("tbody tr")

    row = rows.filter(has_text=nome_material)

    if row.count() == 0:
        return False

    num_patrim = row.last.locator("td[columnid='3']").inner_text()
    
    if ctx.get_by_role("button", name="Menu").is_visible():
        clicar_menu_com_retry(page)
        aguardar_ajax_global(page)
    else:
        page.get_by_title("Home").click()
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

    if ctx.get_by_role("button", name="Menu").is_visible():
        clicar_menu_com_retry(page)
        aguardar_ajax_global(page)
    else:
        page.get_by_title("Home").click()
        aguardar_ajax_global(page)

    return num_patrim
