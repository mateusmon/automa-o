from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_ul(page: Page) -> None:
    acessar_universal(
        page,
        "Estrutura Organizacional - UL - Unidade de Localização",
        caminho_v3=[
            "a:has-text('Corporativo')",
            "a:text-is('Estrutura Organizacional')",
            "a:text-is('UL - Unidade de Localização')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Corporativo'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Estrutura Organizacional'):visible",
            "div.menu-text:text-is('UL - Unidade de Localização'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
