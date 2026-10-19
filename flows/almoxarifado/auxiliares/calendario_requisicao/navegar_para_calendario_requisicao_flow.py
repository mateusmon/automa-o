from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_calendario_requisicao(page: Page) -> None:
    acessar_universal(
        page,
        "Calendário de Requisição",
        caminho_v3=[
            "a:text-is('Almoxarifado')",
            "a:text-is('Auxiliares')",
            ".menu-link > a[title='Calendário de Requisição']"
        ],
        caminho_v4=[
            "div.module-text:text-is('Almoxarifado'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Auxiliares'):visible",
            "div.menu-text:text-is('Calendário de Requisição'):visible",
            "i.mdi.mdi-select-compare:visible"
        ]
    )

