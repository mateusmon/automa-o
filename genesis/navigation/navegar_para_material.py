import re

from playwright.sync_api import Page

from navigation.acessar_universal import acessar_universal
from utils.versao_gen import escopo, get_versao


def heading_material_visivel(page: Page) -> bool:
    if get_versao() >= 4:
        return page.get_by_role(
            "heading", name=re.compile(r"Material - Consumo", re.IGNORECASE)
        ).is_visible()
    return escopo(page).get_by_role(
        "heading", name=re.compile(r"Tabelas - Material Consumo|Material Consumo", re.IGNORECASE)
    ).is_visible()


def acessar_material(page: Page) -> bool:
    if heading_material_visivel(page):
        return True

    return acessar_universal(
        page,
        "Material - Consumo",
        caminho_v3=[
            "a:text-is('Corporativo')",
            "a:has-text('Material / Serviço')",
            "a[id^='menuItemLink']:has-text('Consumo')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Corporativo'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Material'):visible",
            "div.menu-text:text-is('Consumo'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
