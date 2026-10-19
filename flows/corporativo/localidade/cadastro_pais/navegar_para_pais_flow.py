from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_pais(page: Page) -> None:
    acessar_universal(
        page,
        "Localidade - País",
        caminho_v3=[
            "a:has-text('Corporativo')",
            "a:has-text('Localidade')",
            "a:has-text('País')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Corporativo'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Localidade'):visible",
            "div.menu-text:text-is('País'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
