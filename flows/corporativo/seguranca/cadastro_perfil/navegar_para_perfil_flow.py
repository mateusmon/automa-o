from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_perfil(page: Page) -> None:
    acessar_universal(
        page,
        "Segurança - Perfil",
        caminho_v3=[
            "a:has-text('Corporativo')",
            "a:has-text('Segurança')",
            "a:text-is('Perfil')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Corporativo'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Segurança'):visible",
            "div.menu-text:text-is('Perfil'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
