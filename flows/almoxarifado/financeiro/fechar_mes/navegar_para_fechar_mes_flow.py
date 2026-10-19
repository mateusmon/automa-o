from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_fechar_mes(page: Page) -> None:
    return acessar_universal(
        page,
        "Financeiro - Filtro",
        caminho_v3=(
            "a:text-is('Almoxarifado')",
            "a:text-is('Financeiro')",
            ".menu-link > a[title='Fechar/Abrir Mês']",
        ),
        caminho_v4=(
            "div.module-text:text-is('Almoxarifado'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Financeiro'):visible",
            "div.menu-text:text-is('Ano/Mês Referência UG'):visible",
            "i.mdi.mdi-select-compare:visible",
        ),
    )
