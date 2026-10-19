import re

from playwright.sync_api import Page

from navigation.acessar_universal import acessar_universal
from utils.versao_gen import escopo, get_versao


def heading_endereco_visivel(page: Page) -> bool:
    if get_versao() >= 4:
        return page.get_by_role(
            "heading", name=re.compile(r"Localidade - Endereço", re.IGNORECASE)
        ).is_visible()
    return escopo(page).get_by_role(
        "heading", name=re.compile(r"Localidade - Endereço|Endereço", re.IGNORECASE)
    ).is_visible()


def acessar_endereco(page: Page) -> bool:
    if heading_endereco_visivel(page):
        return True

    return acessar_universal(
        page,
        "Localidade - Endereço",
        caminho_v3=[
            "a:text-is('Corporativo')",
            "a:has-text('Localidade')",
            "a:has-text('Endereço')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Corporativo'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:has-text('Localidade'):visible",
            "div.menu-text:has-text('Endereço'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
