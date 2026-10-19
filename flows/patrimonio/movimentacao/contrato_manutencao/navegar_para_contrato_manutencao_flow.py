from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_contrato_manutencao(page: Page) -> None:
    acessar_universal(
        page,
        "Auxiliares - Contrato de Manutenção",
        caminho_v3=[
            "a:is(:has-text('Mobiliário'), :has-text('Patrimônio')) >> nth=0",
            "a:text-is('Movimentação')",
            "a:text-is('Contrato de Manutenção')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Patrimônio'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Auxiliares'):visible",
            "div.menu-text:text-is('Contrato de Manutenção'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
