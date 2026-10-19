from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_grafico_aquisicoes(page: Page) -> None:
    acessar_universal(
        page,
        "Relatórios - Gráfico das aquisições",
        caminho_v3=[
            "a:is(:has-text('Mobiliário'), :has-text('Patrimônio')) >> nth=0",
            "a:text-is('Relatórios')",
            "a:text-is('Gráfico de Distribuição das Aquisições')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Patrimônio'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Relatórios'):visible",
            "div.menu-text:text-is('Gráfico das aquisições'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
