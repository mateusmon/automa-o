from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_adicao_bem_principal(page: Page) -> None:
    acessar_universal(
        page,
        "Movimentação - Adição ao Bem Principal",
        caminho_v3=[
            "a:is(:has-text('Mobiliário'), :has-text('Patrimônio')) >> nth=0",
            "a:text-is('Movimentação')",
            "a:text-is('Adição a Bem Principal')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Patrimônio'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Movimentação'):visible",
            "div.menu-text:text-is('Adição ao Bem Principal'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
