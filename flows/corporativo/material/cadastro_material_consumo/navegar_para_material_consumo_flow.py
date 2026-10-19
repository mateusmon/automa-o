from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_material_consumo(page: Page) -> None:
    acessar_universal(
        page,
        "Material - Consumo",
        caminho_v3=[
            "a:has-text('Corporativo')",
            "a:has-text('Material / Serviço')",
            "a:has-text('Consumo')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Corporativo'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Material'):visible",
            "div.menu-text:text-is('Consumo'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
