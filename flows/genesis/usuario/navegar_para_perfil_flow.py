"""Navegação opcional de Perfil reutilizada pelas garantias de Perfis e Usuários."""

import re

from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal
from utils.versao import escopo, get_versao


def heading_perfil_visivel(page: Page) -> bool:
    """Confere se a página de Perfil já está aberta na versão ativa."""
    if get_versao() >= 4:
        return page.get_by_role(
            "heading", name=re.compile(r"Segurança - Perfil", re.IGNORECASE)
        ).is_visible()
    return escopo(page).get_by_role(
        "heading", name=re.compile(r"Segurança - Perfil|Perfil", re.IGNORECASE)
    ).is_visible()


def acessar_perfil(page: Page) -> bool:
    """Acessa Perfil, retornando False se o menu não existir. Cenário B."""
    if heading_perfil_visivel(page):
        return True

    encontrou = acessar_universal(
        page,
        "Segurança - Perfil",
        caminho_v3=[
            "a:text-is('Corporativo')",
            "a:has-text('Segurança'):visible",
            "a:has-text('Perfil')",
        ],
        caminho_v4=[
            "div.module-text:text-is('Corporativo'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:has-text('Segurança'):visible",
            "div.menu-text:has-text('Perfil'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
        opcional=True,
    )
    return encontrou
