from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_definicao_motivos(page: Page) -> None:
    return acessar_universal(
        page,
        "Auxiliares - Motivos de Saída Temporária",
        caminho_v3=[
            "a:is(:has-text('Mobiliário'), :has-text('Patrimônio')) >> nth=0",
            "a:text-is('Auxiliares')",
            "a:has-text('Motivos de Saída Temporária')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Patrimônio'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Auxiliares'):visible",
            "div.menu-text:text-is('Motivos de Saída Temporária'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
