from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_funcao(page: Page) -> None:
    acessar_universal(
        page,
        "Funcionário - Funções",
        caminho_v3=[
            "a:has-text('Corporativo')",
            "a:has-text('Funcionári')",
            "a:has-text('Cadastro de Funções')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Corporativo'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Funcionário'):visible",
            "div.menu-text:text-is('Funções'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
