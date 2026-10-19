import re

from playwright.sync_api import Page

from navigation.acessar_universal import acessar_universal
from utils.versao_gen import escopo, get_versao


def heading_centro_custo_visivel(page: Page) -> bool:
    if get_versao() >= 4:
        return page.get_by_role(
            "heading", name=re.compile(r"Estrutura Organizacional - CC", re.IGNORECASE)
        ).is_visible()
    return escopo(page).get_by_role(
        "heading", name=re.compile(r"Estrutura [Oo]rganizacional - C\.?C\.?|Centro de Custo", re.IGNORECASE)
    ).is_visible()


def acessar_centro_custo(page: Page) -> bool:
    if heading_centro_custo_visivel(page):
        return True

    return acessar_universal(
        page,
        "Estrutura Organizacional - CC",
        caminho_v3=[
            "a:text-is('Corporativo')",
            "a:text-is('Estrutura Organizacional')",
            "a:has-text('CC - Centro de Custos')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Corporativo'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:has-text('Estrutura Organizacional'):visible",
            "div.menu-text:has-text('CC - Centro de Custos'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
