from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_enderecamento_material(page: Page) -> None:
    acessar_universal(
        page,
        "Auxiliares - Endereçamento de Material",
        caminho_v3=[
            "a:text-is('Almoxarifado')",
            "a:text-is('Auxiliares')",
            ".menu-link > a[title='Endereçamento de Material']"
        ],
        caminho_v4=[
            "div.module-text:text-is('Almoxarifado'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Auxiliares'):visible",
            "div.menu-text:text-is('Endereçamento de Material'):visible",
            "i.mdi.mdi-select-compare:visible"
        ]
    )
