from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_definicao_caracteristica(page: Page) -> None:
    acessar_universal(
        page,
        "Característica do Bem - Definição",
        caminho_v3=[
            "a:has-text('Corporativo')",
            "a:text-is('Característica do bem')",
            "a:text-is('Definição')"
        ],
        caminho_v4=[
            "div.module-text:text-is('Corporativo'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Característica do Bem'):visible",
            "div.menu-text:text-is('Definição'):visible",
            "i.mdi.mdi-select-compare:visible"
        ]
    )
