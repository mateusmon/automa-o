from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_conta_contabil(page: Page) -> None:
    acessar_universal(
        page,
        "Auxiliares - Conta Contábil",
        caminho_v3=[
            "a:text-is('Almoxarifado')",
            "a:text-is('Auxiliares')",
            "a[id^='menuItemLink']:has-text('Conta') >> nth=0"
        ],
        caminho_v4=[
            "div.module-text:text-is('Almoxarifado'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Auxiliares'):visible",
            "div.menu-text:text-is('Conta Contábil'):visible",
            "i.mdi.mdi-select-compare:visible"
        ]
    )
