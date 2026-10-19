from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_definicao_caracteristicas(page: Page) -> bool:
    return acessar_universal(
        page,
        "Auxiliares - Definição das Características",
        caminho_v3=[
            "a:text-is('Almoxarifado')",
            "a:text-is('Auxiliares')",
            ".menu-link > a[title='Definição das Características']",
        ],
        caminho_v4=[
            "div.module-text:text-is('Almoxarifado'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Auxiliares'):visible",
            "div.menu-text:text-is('Definição das Características'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
        opcional=True,
    )
