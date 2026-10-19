from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_intervalo_n_patrimoniais(page: Page) -> None:
    return acessar_universal(
        page,
        "Auxiliares - Intervalo de Nº Patrimoniais",
        caminho_v3=[
            "a:is(:has-text('Mobiliário'), :has-text('Patrimônio')) >> nth=0",
            "a:text-is('Auxiliares')",
            "a:has-text('Intervalo')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Patrimônio'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Auxiliares'):visible",
            "div.menu-text:has-text('Intervalo'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
