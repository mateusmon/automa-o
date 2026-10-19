from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_situacao_fisica(page: Page) -> bool:
    return acessar_universal(
        page,
        "Auxiliares - Situação Física",
        caminho_v3=[
            "a:is(:has-text('Mobiliário'), :has-text('Patrimônio')) >> nth=0",
            "a:text-is('Auxiliares')",
            "a:has-text('Situação Física')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Patrimônio'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Auxiliares'):visible",
            "div.menu-text:text-is('Situação Física'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
        opcional=True,
    )
