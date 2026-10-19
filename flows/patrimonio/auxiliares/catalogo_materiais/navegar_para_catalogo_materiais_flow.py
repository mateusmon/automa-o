from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_catalogo_materiais(page: Page) -> None:
    return acessar_universal(
        page,
        "Auxiliares - Catálogo de Materiais",
        caminho_v3=[
            "a:is(:has-text('Mobiliário'), :has-text('Patrimônio')) >> nth=0",
            "a:text-is('Auxiliares')",
            "a:has-text('Catálogo de Materiais')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Patrimônio'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Auxiliares'):visible",
            "div.menu-text:text-is('Catálogo de Materiais'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
