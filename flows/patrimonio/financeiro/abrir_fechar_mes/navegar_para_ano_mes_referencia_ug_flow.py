from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_ano_mes_referencia(page: Page) -> None:
    acessar_universal(
        page,
        "Financeiro - Ano/ Mês Referência UG",
        caminho_v3=[
            "a:is(:has-text('Mobiliário'), :has-text('Patrimônio')) >> nth=0",
            "a:text-is('Financeiro')",
            "a:has-text('Ano/Mês Referência Ug')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Patrimônio'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Financeiro'):visible",
            "div.menu-text:text-is('Ano/ Mês Referência UG'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
