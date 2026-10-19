import re

from playwright.sync_api import Page

from navigation.acessar_universal import acessar_universal
from utils.versao_gen import escopo, get_versao


def heading_almoxarifado_visivel(page: Page) -> bool:
    if get_versao() >= 4:
        return page.get_by_role(
            "heading", name=re.compile(r"Estrutura Organizacional - Almoxarifado", re.IGNORECASE)
        ).is_visible()
    return escopo(page).get_by_role(
        # Foi necessário modificar o heading, pois não estava funcionando no MPF.
        # Verificar se o "|Almoxarifado" ainda é necessário.
        #"heading", name=re.compile(r"Estrutura [Oo]rganizacional - Almoxarifado|Almoxarifado", re.IGNORECASE)
        "heading", name=re.compile(r"Estrutura [Oo]rganizacional - Almoxarifado", re.IGNORECASE)
    ).is_visible()


def acessar_almoxarifado(page: Page) -> bool:
    if heading_almoxarifado_visivel(page):
        return True

    return acessar_universal(
        page,
        "Estrutura Organizacional - Almoxarifado",
        caminho_v3=[
            "a:text-is('Corporativo')",
            "a:text-is('Estrutura Organizacional')",
            ".menu-link > a[title='Almoxarifado']",
        ],
        caminho_v4=[
            "div.module-text:text-is('Corporativo'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Estrutura Organizacional'):visible",
            "div.menu-text:text-is('Almoxarifado'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
    )
