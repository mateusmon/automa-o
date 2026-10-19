from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_atendimento_requisicao(page: Page) -> None:
    acessar_universal(
        page,
        "Movimentação - Requisição - Atendimento",
        caminho_v3=[
            "a:text-is('Almoxarifado')",
            "a:text-is('Movimentação Interna')",
            ".menu-link > a[title='Atendimento de Requisição']"
        ],
        caminho_v4=[
            "div.module-text:text-is('Almoxarifado'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Movimentação'):visible",
            "div.menu-text:text-is('Requisição'):visible",
            "div.menu-text:text-is('Atendimento'):visible",
            "i.mdi.mdi-select-compare:visible"
        ]
    )