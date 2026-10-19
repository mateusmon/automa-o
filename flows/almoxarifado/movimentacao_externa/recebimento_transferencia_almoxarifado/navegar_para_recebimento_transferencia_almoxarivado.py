from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_recebimento_transferencia_almoxarifado(page: Page) -> None:
    acessar_universal(
        page,
        "Movimentação - Transferência Externa - Recebimento",
        caminho_v3=[
            "a:text-is('Almoxarifado')",
            "a:text-is('Movimentação Externa')",
            ".menu-link > a[title='Recebimento da Transferência entre Almoxarifado']"
        ],
        caminho_v4=[
            "div.module-text:text-is('Almoxarifado'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Movimentação'):visible",
            "div.menu-text:text-is('Transferência Externa'):visible",
            "div.menu-text:text-is('Recebimento'):visible",
            "i.mdi.mdi-select-compare:visible"
        ]
    )
