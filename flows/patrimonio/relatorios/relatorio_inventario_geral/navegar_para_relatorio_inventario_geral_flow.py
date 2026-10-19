from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_relatorio_inventario_geral(page: Page) -> None:
    acessar_universal(
        page,
        "Relatórios - Inventário",
        caminho_v3=[
            "a:is(:has-text('Mobiliário'), :has-text('Patrimônio')) >> nth=0",
            "a:text-is('Relatórios')",
            "a:text-is('Relatório Inventário Geral')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Patrimônio'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Relatórios'):visible",
            "div.menu-content > div.menu-item:has(div.menu-text:text-is('Inventário'))",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
