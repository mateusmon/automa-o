from playwright.sync_api import expect

from utils.waits import esperar_pagina_carregar, preencher_autocomplete


def cadastrar_requisicao(page, dados):

    ur_padrao = list(dados["urs"].values())[0]
    almoxarifado = list(dados["almoxarifados"].values())[0]
    material = list(dados["materiais"].values())[0]

    page.get_by_role("link", name="Almoxarifado").click()
    page.get_by_role("link", name="Movimentação Interna").nth(0).click()
    page.get_by_text("Cadastro de Requisição", exact=True).click()

    esperar_pagina_carregar(page)

    expect(page.get_by_role("heading", name="Requisição")).to_be_visible()

    #for material in list(dados["materiais"].values()):
    for n in range(5):

        preencher_autocomplete(page, 'input[name="ur"]', ur_padrao["codigo"])

        preencher_autocomplete(page, 'input[name="almoxarifado"]', almoxarifado["codigo"])

        preencher_autocomplete(page, 'input[name="bemServico-1"]', material["codigo"])

        # quantidade
        page.locator('input[name="qtRequisicao-2-5"]').fill("1")

        page.get_by_role("button", name="Confirmar").click()

        esperar_pagina_carregar(page)

        page.get_by_role("button", name="Novo").click()

        esperar_pagina_carregar(page)
