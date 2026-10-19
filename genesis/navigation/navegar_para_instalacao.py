import re

from playwright.sync_api import Page

from navigation.acessar_universal import acessar_universal
from utils.versao_gen import escopo, get_versao


def heading_instalacao_visivel(page: Page) -> bool:
    if get_versao() >= 4:
        return page.get_by_role(
            "heading", name=re.compile(r"Localidade - Instalação", re.IGNORECASE)
        ).is_visible()
    return escopo(page).get_by_role(
        "heading", name=re.compile(r"Localidade - Instalação|Instalação", re.IGNORECASE)
    ).is_visible()


def acessar_instalacao(page: Page) -> bool:
    if heading_instalacao_visivel(page):
        return True

    return acessar_universal(
        page,
        "Localidade - Instalação",
        caminho_v3=[
            "a:text-is('Corporativo')",
            "a:has-text('Localidade')",
            "a:has-text('Instalação')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Corporativo'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:has-text('Localidade'):visible",
            "div.menu-text:has-text('Instalação'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
