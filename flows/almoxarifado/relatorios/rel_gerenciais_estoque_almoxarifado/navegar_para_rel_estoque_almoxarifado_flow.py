from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_rel_gerenciais_estoque_almoxarifado(page: Page) -> None:
    return acessar_universal(
        page,
        "Rel. Gerenciais - Estoque de Almoxarifado.",
        caminho_v3=(
            "a:text-is('Almoxarifado')",
            "a:text-is('Relatórios')",
            ".menu-link > a[title='Rel. Gerenciais - Estoque de Almoxarifado']",
        ),
        caminho_v4=(
            "div.module-text:text-is('Almoxarifado'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Relatórios'):visible",
            "div.menu-text:text-is('Estoque de Almoxarifado'):visible",
            "i.mdi.mdi-select-compare:visible",
        ),
    )
