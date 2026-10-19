from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_classificacao_material(page: Page) -> None:
    acessar_universal(
        page,
        "Gestão de Estoque - Classificação do Material",
        caminho_v3=[
                "a:text-is('Almoxarifado')",
                "a:text-is('Gestão de Estoque')",
                ".menu-link > a[title='Classificação do Material']"
            ],
        caminho_v4=[
                "div.module-text:text-is('Almoxarifado'):visible",
                "i.mdi.mdi-select-compare:visible",
                "div.menu-text:text-is('Gestão de Estoque'):visible",
                "div.menu-text:text-is('Classificação do Material'):visible",
                "i.mdi.mdi-select-compare:visible"
            ]
        )
