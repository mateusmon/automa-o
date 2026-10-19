from playwright.sync_api import Page

from navigation.acessar_universal import acessar_universal


def acessar_evento(page: Page) -> bool:
    return acessar_universal(
        page,
        "Gestão de Compras - Evento",
        caminho_v3=(
            "a:text-is('Almoxarifado')",
            "a:text-is('Gestão de Compras')",
            ".menu-link > a[title='Evento']",
        ),
        caminho_v4=(
            "div.module-text:text-is('Almoxarifado'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Gestão de Compras'):visible",
            "div.menu-text:text-is('Evento'):visible",
            "i.mdi.mdi-select-compare:visible",
        ),
    )
