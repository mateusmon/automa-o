from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_rmb(page: Page) -> None:
    acessar_universal(
        page,
        "Financeiro - Resumo Mensal de Bens-RMB",
        caminho_v3=[
            "a:is(:has-text('Mobiliário'), :has-text('Patrimônio')) >> nth=0",
            "a:text-is('Financeiro')",
            "a:has-text('Resumo Mensal de Bens (RMB)')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Patrimônio'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Financeiro'):visible",
            "div.menu-text:text-is('Resumo Mensal de Bens-RMB'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
