import re

from playwright.sync_api import Page

from navigation.acessar_universal import acessar_universal
from utils.versao_gen import escopo, get_versao


def heading_fornecedor_visivel(page: Page) -> bool:
    if get_versao() >= 4:
        return page.get_by_role(
            "heading", name=re.compile(r"Entidade Externa - Fornecedor", re.IGNORECASE)
        ).is_visible()
    return escopo(page).get_by_role(
        "heading", name=re.compile(r"Fornecedor", re.IGNORECASE)
    ).is_visible()


def acessar_fornecedor(page: Page) -> bool:
    if heading_fornecedor_visivel(page):
        return True

    return acessar_universal(
        page,
        "Entidade Externa - Fornecedor",
        caminho_v3=[
            "a:text-is('Corporativo')",
            "a:has-text('Entidade externa')",
            "a[id^='menuItemLink']:has-text('Cadastro de Fornecedor')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Corporativo'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Entidade Externa'):visible",
            "div.menu-text:text-is('Fornecedor'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
