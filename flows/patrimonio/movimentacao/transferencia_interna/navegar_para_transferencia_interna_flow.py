from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_transferencia_interna(page: Page) -> None:
    acessar_universal(
        page,
        "Movimentação - Transferência Interna - Cadastro",
        caminho_v3=[
            "a:is(:has-text('Mobiliário'), :has-text('Patrimônio')) >> nth=0",
            "a:text-is('Movimentação')",
            "a:text-is('Transferência Interna')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Patrimônio'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Movimentação'):visible",
            "div.menu-text:text-is('Transferência Interna'):visible",
            "div.menu-text:text-is('Cadastro'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
