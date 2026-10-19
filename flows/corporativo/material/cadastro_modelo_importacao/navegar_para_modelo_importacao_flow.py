from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_modelo_importacao(page: Page) -> None:
    acessar_universal(
        page,
        "Material - Modelo de Importação",
        caminho_v3=[
            "a:has-text('Corporativo')",
            "a:has-text('Material / Serviço')",
            "a:text-is('Modelo de Importação')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Corporativo'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Material'):visible",
            "div.menu-text:text-is('Modelo de Importação'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
