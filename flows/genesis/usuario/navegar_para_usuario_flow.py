"""Navegação de Usuário com retorno opcional exigido por garantir_usuarios."""

import re

from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal
from utils.versao import escopo, get_versao


def heading_usuario_visivel(page: Page) -> bool:
    """Confere se a página de Usuário já está aberta na versão ativa."""
    if get_versao() >= 4:
        return page.get_by_role(
            "heading", name=re.compile(r"Segurança - Usuário", re.IGNORECASE)
        ).is_visible()
    return escopo(page).get_by_role(
        "heading", name=re.compile(r"Segurança - Usuário|Usuário", re.IGNORECASE)
    ).is_visible()


def acessar_usuario(page: Page) -> bool:
    """Acessa Usuário, retornando False se o menu não existir. Cenário B."""
    if heading_usuario_visivel(page):
        return True

    encontrou = acessar_universal(
        page,
        "Segurança - Usuário",
        caminho_v3=[
            "a:text-is('Corporativo')",
            "a:has-text('Segurança'):visible",
            "div.menu-link a[url*='UsuarioEditGateway']:visible",
        ],
        caminho_v4=[
            "div.module-text:text-is('Corporativo'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:has-text('Segurança'):visible",
            "div.menu-text:text-is('Usuário'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
        opcional=True,
    )
    return encontrou
