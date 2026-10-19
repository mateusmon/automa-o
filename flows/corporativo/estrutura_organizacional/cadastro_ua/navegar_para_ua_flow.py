from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_ua(page: Page) -> None:
    acessar_universal(
        page,
        "Estrutura Organizacional - UA - Unidade Administrativa",
        caminho_v3=[
            "a:has-text('Corporativo')",
            "a:text-is('Estrutura Organizacional')",
            "a:text-is('UA - Unidade Administrativa')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Corporativo'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Estrutura Organizacional'):visible",
            "div.menu-text:text-is('UA - Unidade Administrativa'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
