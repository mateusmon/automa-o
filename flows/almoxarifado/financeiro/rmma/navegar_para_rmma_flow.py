from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_rmma(page: Page) -> None:
    return acessar_universal(
        page,
        "Consultar Financeiro - RMMA/RMAA",
        caminho_v3=(
            "a:text-is('Almoxarifado')",
            "a:text-is('Financeiro')",
            ".menu-link > a:has-text('Relatório RMMA')",
        ),
        caminho_v4=(
            "div.module-text:text-is('Almoxarifado'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Financeiro'):visible",
            "div.menu-text:text-is('RMMA/RMAA'):visible",
            "i.mdi.mdi-select-compare:visible",
        ),
    )
