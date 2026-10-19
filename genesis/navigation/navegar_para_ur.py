import re

from playwright.sync_api import Page

from navigation.acessar_universal import acessar_universal
from utils.versao_gen import escopo, get_versao


def heading_ur_visivel(page: Page) -> bool:
    if get_versao() >= 4:
        return page.get_by_role(
            "heading", name=re.compile(r"Estrutura Organizacional - UR", re.IGNORECASE)
        ).is_visible()
    return escopo(page).get_by_role(
        "heading", name=re.compile(r"Estrutura Organizacional - U\.?R\.?", re.IGNORECASE)
    ).is_visible()


def acessar_ur(page: Page) -> bool:
    if heading_ur_visivel(page):
        return True

    return acessar_universal(
        page,
        "Estrutura Organizacional - UR",
        caminho_v3=[
            "a:text-is('Corporativo')",
            "a:text-is('Estrutura Organizacional')",
            "a:has-text('UR - Unidade de Requisição')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Corporativo'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:has-text('Estrutura Organizacional'):visible",
            "div.menu-text:has-text('UR - Unidade de Requisição'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
