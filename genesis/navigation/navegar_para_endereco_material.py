import re

from playwright.sync_api import Page

from navigation.acessar_universal import acessar_universal
from utils.versao_gen import escopo, get_versao


def heading_endereco_material_visivel(page: Page) -> bool:
    if get_versao() >= 4:
        return page.get_by_role(
            "heading", name=re.compile(r"Auxiliares - Endereço de", re.IGNORECASE)
        ).is_visible()
    return escopo(page).get_by_role(
        "heading", name=re.compile(r"Tabelas - Estoque - Endereço", re.IGNORECASE)
    ).is_visible()


def acessar_endereco_material(page: Page) -> bool:
    if heading_endereco_material_visivel(page):
        return True

    return acessar_universal(
        page,
        "Auxiliares - Endereço de Estoque",
        caminho_v3=[
            "a:text-is('Almoxarifado')",
            "a:text-is('Auxiliares')",
            ".menu-link > a[title='Endereço de Estoque']",
        ],
        caminho_v4=[
            "div.module-text:text-is('Almoxarifado'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Auxiliares'):visible",
            "div.menu-text:text-is('Endereço de Estoque'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
