from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_cidade(page: Page) -> None:
    acessar_universal(
        page,
        "Localidade - Cidade",
        caminho_v3=[
            "a:has-text('Corporativo')",
            "a:has-text('Localidade')",
            "a:has-text('Cidade')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Corporativo'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Localidade'):visible",
            "div.menu-text:text-is('Cidade'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
