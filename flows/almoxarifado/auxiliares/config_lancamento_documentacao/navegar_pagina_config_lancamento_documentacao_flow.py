from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_config_documentacao(page: Page) -> None:
    acessar_universal(
        page,
        "Auxiliares - Configuração Lançamentos - Documentação",
        caminho_v3=[
            "a:text-is('Almoxarifado')",
            "a:text-is('Auxiliares')",
            ".menu-link > a[title='Configuração Lançamentos - Documentação']"
        ],
        caminho_v4=[
            "div.module-text:text-is('Almoxarifado'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Auxiliares'):visible",
            "div.menu-text:text-is('Documentação'):visible",
            "i.mdi.mdi-select-compare:visible"
        ]
    )
