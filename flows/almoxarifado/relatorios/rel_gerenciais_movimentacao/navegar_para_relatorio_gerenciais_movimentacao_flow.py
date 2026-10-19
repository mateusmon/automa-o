from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_relatorio_gerenciais_movimentacao(page: Page) -> None:
    return acessar_universal(
        page,
        "Rel. Gerenciais - Movimentação",
        caminho_v3=(
            "a:text-is('Almoxarifado')",
            "a:text-is('Relatórios')",
            ".menu-link > a[title='Rel. Gerenciais - Movimentação']",
        ),
        caminho_v4=(
            "div.module-text:text-is('Almoxarifado'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Relatórios'):visible",
            "div.menu-item > div.menu-text:text-is('Movimentação'):visible",
            "i.mdi.mdi-select-compare:visible",
        ),
    )
