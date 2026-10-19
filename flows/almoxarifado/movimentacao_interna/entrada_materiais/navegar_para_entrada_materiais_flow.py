from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_entrada_materiais(page: Page) -> None:
    acessar_universal(
        page,
        "Movimentação - Entrada de Material",
        caminho_v3=[
            "a:text-is('Almoxarifado')",
            "a:text-is('Movimentação Interna')",
            ".menu-link > a[title='Entrada de Materiais']"
        ],
        caminho_v4=[
            "div.module-text:text-is('Almoxarifado'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Movimentação'):visible",
            "div.menu-text:has-text('Entrada de Material'):visible",
            "i.mdi.mdi-select-compare:visible"
        ]
    )