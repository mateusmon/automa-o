from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_formacao_comissao_inventario(page: Page) -> None:
    acessar_universal(
        page,
        "Inventário - Formação de Comissão",
        caminho_v3=[
            "a:is(:has-text('Mobiliário'), :has-text('Patrimônio')) >> nth=0",
            "a:text-is('Inventário')",
            "a:has-text('Formação de Comissão')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Patrimônio'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Inventário'):visible",
            "div.menu-text:text-is('Formação de Comissão'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
