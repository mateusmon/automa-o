from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_material_etiquetas(page: Page) -> None:
    return acessar_universal(
        page,
        "Material - Etiquetas",
        caminho_v3=(
            "a:text-is('Almoxarifado')",
            "a:text-is('Relatórios')",
            ".menu-link > a[title='Material - Etiquetas']",
        ),
        caminho_v4=(
            "div.module-text:text-is('Almoxarifado'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Relatórios'):visible",
            "div.menu-text:text-is('Material - Etiquetas'):visible",
            "i.mdi.mdi-select-compare:visible",
        ),
    )
