from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_emissao_termo_responsabilidade(page: Page) -> None:
    return acessar_universal(
        page,
        "Termo de Responsabilidade - Emissão",
        caminho_v3=[
            "a:is(:has-text('Mobiliário'), :has-text('Patrimônio')) >> nth=0",
            "a:text-is('Termo de Responsabilidade')",
            "a:has-text('Emissão do Termo de Responsabilidade')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Patrimônio'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Termo de Responsabilidade'):visible",
            "div.menu-text:text-is('Emissão'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
