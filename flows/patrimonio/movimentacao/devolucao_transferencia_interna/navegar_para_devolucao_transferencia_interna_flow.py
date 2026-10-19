from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_devolucao_transferencia_interna(page: Page) -> bool:
    return acessar_universal(
        page,
        "Movimentação - Transferência Interna - Devolução",
        caminho_v3=[
            "a:is(:has-text('Mobiliário'), :has-text('Patrimônio')) >> nth=0",
            "a:text-is('Movimentação')",
            "a:text-is('Devolução da Transferência Interna')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Patrimônio'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Movimentação'):visible",
            "div.menu-text:text-is('Transferência Interna'):visible",
            "div.menu-text:text-is('Devolução'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
        opcional=True,
    )
