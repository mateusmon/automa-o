from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_fornecedor(page: Page) -> None:
    acessar_universal(
        page,
        "Entidade Externa - Fornecedor",
        caminho_v3=[
            "a:has-text('Corporativo')",
            "a:text-is('Entidade externa')",
            "a:has-text('Cadastro de Fornecedor')"
        ],
        caminho_v4=[
            "div.module-text:text-is('Corporativo'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Entidade Externa'):visible",
            "div.menu-text:text-is('Fornecedor'):visible",
            "i.mdi.mdi-select-compare:visible"
        ]
    )
