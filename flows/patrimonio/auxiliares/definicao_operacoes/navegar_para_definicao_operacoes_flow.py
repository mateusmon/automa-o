from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_definicao_operacoes(page: Page) -> None:
    return acessar_universal(
        page,
        "Auxiliares - Definição das Operações",
        caminho_v3=[
            "a:is(:has-text('Mobiliário'), :has-text('Patrimônio')) >> nth=0",
            "a:text-is('Auxiliares')",
            "a:has-text('Definição das Operações')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Patrimônio'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Auxiliares'):visible",
            "div.menu-text:text-is('Operações'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
