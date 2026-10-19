from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_requisicao_bens(page: Page) -> bool:
    return acessar_universal(
        page,
        "Movimentação - Requisição - Cadastro",
        caminho_v3=[
            "a:is(:has-text('Mobiliário'), :has-text('Patrimônio')) >> nth=0",
            "a:text-is('Movimentação')",
            "a:text-is('Requisição de Bens')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Patrimônio'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Movimentação'):visible",
            "div.menu-text:text-is('Requisição'):visible",
            "div.menu-text:text-is('Cadastro'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
        opcional=True,
    )
