import re

from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal
from utils.versao import escopo, get_versao


def heading_enderecamento_visivel(page: Page) -> bool:
    """Confere se a página de Endereçamento de Material já está aberta."""
    if get_versao() >= 4:
        return page.get_by_role(
            "heading", name=re.compile(r"Auxiliares - Endereçamento de", re.IGNORECASE)
        ).is_visible()
    return escopo(page).get_by_role(
        "heading", name=re.compile(r"Material - Endereço", re.IGNORECASE)
    ).is_visible()


def acessar_enderecamento(page: Page) -> bool:
    """Acessa Endereçamento de Material, evitando repetir a navegação se já aberto."""
    if heading_enderecamento_visivel(page):
        return True

    encontrou = acessar_universal(
        page,
        "Auxiliares - Endereçamento de Material",
        caminho_v3=[
            "a:text-is('Almoxarifado')",
            "a:text-is('Auxiliares')",
            ".menu-link > a[title='Endereçamento de Material']",
        ],
        caminho_v4=[
            "div.module-text:text-is('Almoxarifado'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Auxiliares'):visible",
            "div.menu-text:text-is('Endereçamento de Material'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
    return encontrou
