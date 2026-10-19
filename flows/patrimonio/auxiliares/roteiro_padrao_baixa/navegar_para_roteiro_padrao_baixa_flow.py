from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_roteiro_padrao_baixa(page: Page) -> bool:
    return acessar_universal(
        page,
        "Roteiro Padrão de Baixa",
        caminho_v3=[
            "a:is(:has-text('Mobiliário'), :has-text('Patrimônio')) >> nth=0",
            "a:text-is('Auxiliares')",
            "a:has-text('Roteiro Padrão para Baixa')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Patrimônio'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Movimentação'):visible",
            "div.menu-text:text-is('Baixa'):visible",
            "div.menu-text:text-is('Roteiro Padrão'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
        opcional=True,
    )
