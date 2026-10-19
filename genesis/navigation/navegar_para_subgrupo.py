import re

from playwright.sync_api import Page

from navigation.acessar_universal import acessar_universal
from utils.versao_gen import escopo, get_versao


def heading_subgrupo_visivel(page: Page) -> bool:
    if get_versao() >= 4:
        return page.get_by_role(
            "heading", name=re.compile(r"Material - Supply", re.IGNORECASE)
        ).is_visible()
    return escopo(page).get_by_role(
        "heading", name=re.compile(r"Supply", re.IGNORECASE)
    ).is_visible()


def acessar_subgrupo(page: Page) -> bool:
    if heading_subgrupo_visivel(page):
        return True

    return acessar_universal(
        page,
        "Material - Supply",
        caminho_v3=[
            "a:text-is('Corporativo')",
            "a:text-is('Material / Serviço')",
            ".menu-link > a[title='Supply']",
        ],
        caminho_v4=[
            "div.module-text:text-is('Corporativo'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Material'):visible",
            "div.menu-text:text-is('Supply'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
