from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_outros_relatorios(page: Page) -> None:
    acessar_universal(
        page,
        "Relatórios - Outros",
        caminho_v3=[
            "a:is(:has-text('Mobiliário'), :has-text('Patrimônio')) >> nth=0",
            "a:text-is('Relatórios')",
            "a:text-is('Outros Relatórios')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Patrimônio'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Relatórios'):visible",
            "div.menu-text:text-is('Outros'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
