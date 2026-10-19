from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_baixa_pedido(page: Page) -> bool:
    return acessar_universal(
        page,
        "Gestão de Compras - Pedido de Compras - Baixa",
        caminho_v3=(
            "a:text-is('Almoxarifado')",
            "a:text-is('Gestão de Compras')",
            ".menu-link > a[title='Baixa de Pedido']",
        ),
        caminho_v4=(
            "div.module-text:text-is('Almoxarifado'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Gestão de Compras'):visible",
            "div.menu-text:text-is('Pedido de Compras'):visible",
            "div.menu-text:text-is('Baixa'):visible",
            "i.mdi.mdi-select-compare:visible",
        ),
    )
