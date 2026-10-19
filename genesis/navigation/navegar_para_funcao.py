import re

from playwright.sync_api import Page

from navigation.acessar_universal import acessar_universal
from utils.versao_gen import escopo, get_versao


def heading_funcao_visivel(page: Page) -> bool:
    if get_versao() >= 4:
        return page.get_by_role(
            "heading", name=re.compile(r"Funcionário - Funções", re.IGNORECASE)
        ).is_visible()
    return escopo(page).get_by_role(
        "heading", name=re.compile(r"Funcionário - Funções|Funções", re.IGNORECASE)
    ).is_visible()


def acessar_funcao(page: Page) -> bool:
    if heading_funcao_visivel(page):
        return True

    return acessar_universal(
        page,
        "Funcionário - Funções",
        caminho_v3=[
            "a:text-is('Corporativo')",
            "a:has-text('Funcionári')",
            "a:has-text('Cadastro de Funções')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Corporativo'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:has-text('Funcionário'):visible",
            "div.menu-text:has-text('Funções'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
