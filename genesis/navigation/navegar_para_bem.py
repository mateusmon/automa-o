import re

from playwright.sync_api import Page

from navigation.acessar_universal import acessar_universal
from utils.versao_gen import escopo, get_versao


def heading_bem_visivel(page: Page) -> bool:
    if get_versao() >= 4:
        return page.get_by_role(
            "heading", name=re.compile(r"Material - Permanente", re.IGNORECASE)
        ).is_visible()
    return escopo(page).get_by_role(
        "heading", name=re.compile(r"Material Permanente|Tabelas - Material Permanente", re.IGNORECASE)
    ).is_visible()


def acessar_bem(page: Page, reiniciar_navegacao: bool = False) -> bool:
    if not reiniciar_navegacao and heading_bem_visivel(page):
        return True

    return acessar_universal(
        page,
        "Material - Permanente",
        caminho_v3=[
            "a:text-is('Corporativo')",
            "a:has-text('Material / Serviço')",
            "a[id^='menuItemLink']:has-text('Permanente')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Corporativo'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:has-text('Material'):visible",
            "div.menu-text:has-text('Permanente'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
