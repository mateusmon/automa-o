from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_recebimento_devolucao(page: Page) -> None:
    acessar_universal(
        page,
        "Movimentação - Devolução de Materiais - Recebimento",
        caminho_v3=[
            "a:text-is('Almoxarifado')",
            "a:text-is('Movimentação Interna')",
            ".menu-link > a[title='Recebimento da Devolução de Materiais']"
        ],
        caminho_v4=[
            "div.module-text:text-is('Almoxarifado'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Movimentação'):visible",
            "div.menu-text:text-is('Devolução'):visible",
            "div.menu-text:text-is('Recebimento'):visible",
            "i.mdi.mdi-select-compare:visible"
        ]
    )
