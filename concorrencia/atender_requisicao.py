
from playwright.sync_api import Page, expect

from utils.waits import esperar_pagina_carregar


def atender_requisicao(page: Page, dados):
    
    almoxarifado = list(dados["almoxarifados"].values())[0]
    ur = list(dados["urs"].values())[0]

    page.get_by_role("link", name="Almoxarifado").click()
    page.get_by_role("link", name="Movimentação Interna").nth(0).click()
    page.get_by_text("Atendimento de Requisição").click()
    esperar_pagina_carregar(page)

    expect(page.get_by_role("heading", name="Atendimento de requisição")).to_be_visible()

    while True:

        page.select_option('select[name="almoxarifado"]', value=almoxarifado["codigo"])
        esperar_pagina_carregar(page)

        linhas = page.locator("table.tabelaComRolagem tbody tr").filter(
            has=page.locator("td:nth-child(5)", has_text=ur["codigo"])
        )

        linha = linhas.first

        if linha.count() == 0:
            break        

        linha.locator("td:nth-child(9) input[type='checkbox']").check()

        #time.sleep(random.uniform(0.3, 1.2))

        page.get_by_role("button", name="Automático").click(timeout=90_000)
        
        esperar_pagina_carregar(page)

        if page.locator(".alert-danger").count() > 0:
            continue
        
        page.wait_for_timeout(1000)

        page.get_by_role("button", name="Retornar").click()

        esperar_pagina_carregar(page)
    