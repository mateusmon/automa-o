from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_solicitacao_materiais(page: Page) -> None:
    acessar_universal(
        page,
        "Movimentação - Solicitação de Materiais",
        caminho_v3=[
            "a:text-is('Almoxarifado')",
            "a:text-is('Movimentação Interna')",
            ".menu-link > a[title='Solicitação de Materiais']"
        ],
        caminho_v4=[
            "div.module-text:text-is('Almoxarifado'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Movimentação'):visible",
            "div.menu-text:text-is('Requisição'):visible",
            "div.menu-text:text-is('Solicitação'):visible",
            "i.mdi.mdi-select-compare:visible"
        ]
    )
