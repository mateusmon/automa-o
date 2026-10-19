from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_relatorio_entradas(page: Page) -> None:
    acessar_universal(
        page,
        "Relatórios - Entradas",
        caminho_v3=[
            "a:is(:has-text('Mobiliário'), :has-text('Patrimônio')) >> nth=0",
            "a:text-is('Relatórios')",
            "a:text-is('Relatório de Entradas')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Patrimônio'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Relatórios'):visible",
            "div.menu-text:text-is('Entradas'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
