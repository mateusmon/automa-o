from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_almoxarifado(page: Page) -> None:
    acessar_universal(
        page,
        "Estrutura Organizacional - Almoxarifado",
        caminho_v3=[
            "a:has-text('Corporativo')",
            "a:text-is('Estrutura Organizacional')",
            ".menu-link a:has-text('Almoxarifado')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Corporativo'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Estrutura Organizacional'):visible",
            "div.menu-text:text-is('Almoxarifado'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
