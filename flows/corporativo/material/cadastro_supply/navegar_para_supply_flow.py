from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_supply(page: Page) -> bool:
    return acessar_universal(
        page,
        "Material - Supply",
        caminho_v3=(
            "a:text-is('Corporativo')",
            "a:text-is('Material / Serviço')",
            ".menu-link > a[title='Supply']"
        ),
        caminho_v4=(
            "div.module-text:text-is('Corporativo'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Material'):visible",
            "div.menu-text:text-is('Supply'):visible",
            "i.mdi.mdi-select-compare:visible"
        ),
        opcional=True,
    )
