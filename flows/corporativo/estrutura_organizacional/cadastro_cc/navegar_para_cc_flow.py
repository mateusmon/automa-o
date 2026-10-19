from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_cc(page: Page) -> None:
    acessar_universal(
        page,
        "Estrutura Organizacional - CC - Centro de Custos",
        caminho_v3=[
            "a:has-text('Corporativo')",
            "a:text-is('Estrutura Organizacional')",
            "a:text-is('CC - Centro de Custos')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Corporativo'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Estrutura Organizacional'):visible",
            "div.menu-text:text-is('CC - Centro de Custos'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
