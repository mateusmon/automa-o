from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_modificacao_material(page: Page) -> None:
    return acessar_universal(
        page,
        "Modificação - Material",
        caminho_v3=[
            "a:is(:has-text('Mobiliário'), :has-text('Patrimônio')) >> nth=0",
            "a:text-is('Modificação')",
            "a:has-text('Modificação de Material')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Patrimônio'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Modificação'):visible",
            "div.menu-text:text-is('Material'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
