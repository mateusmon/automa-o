from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_autorizacao_requisicao(page: Page) -> None:
    acessar_universal(
        page,
        "Movimentação - Requisição - Autorização",
        caminho_v3=[
            "a:text-is('Almoxarifado')",
            "a:text-is('Movimentação Interna')",
            ".menu-link > a[title='Autorização de Requisição']"
        ],
        caminho_v4=[
            "div.module-text:text-is('Almoxarifado'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Movimentação'):visible",
            "div.menu-text:text-is('Requisição'):visible",
            "div.menu-text:text-is('Autorização'):visible",
            "i.mdi.mdi-select-compare:visible"
        ]
    )
    