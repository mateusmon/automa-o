import re

from playwright.sync_api import Page

from navigation.acessar_universal import acessar_universal
from utils.versao_gen import escopo, get_versao


def heading_catalogo_visivel(page: Page) -> bool:
    if get_versao() >= 4:
        return page.get_by_role(
            "heading", name=re.compile(r"Auxiliares - Catálogo Restrito", re.IGNORECASE)
        ).is_visible()
    return escopo(page).get_by_role(
        "heading", name=re.compile(r"Catálogo [Dd]e [Mm]aterial|Catálogo Restrito", re.IGNORECASE)
    ).is_visible()


def acessar_catalogo(page: Page) -> bool:
    if heading_catalogo_visivel(page):
        return True

    return acessar_universal(
        page,
        "Auxiliares - Catálogo Restrito",
        caminho_v3=[
            "a:text-is('Almoxarifado')",
            "a:text-is('Auxiliares')",
            "a:has-text('Catálogo Restrito')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Almoxarifado'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:has-text('Auxiliares'):visible",
            "div.menu-text:has-text('Catálogo Restrito'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
