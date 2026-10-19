from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_estorno(page: Page) -> None:
    acessar_universal(
        page,
        "Movimentação - Estorno de Materiais",
        caminho_v3=[
            "a:text-is('Almoxarifado')",
            "a:text-is('Movimentação Interna')",
            ".menu-link > a[title='Estorno de Materiais']"
        ],
        caminho_v4=[
            "div.module-text:text-is('Almoxarifado'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Movimentação'):visible",
            "div.menu-text:text-is('Baixa'):visible",
            "div.menu-text:text-is('Estorno'):visible",
            "i.mdi.mdi-select-compare:visible"
        ]
    )
