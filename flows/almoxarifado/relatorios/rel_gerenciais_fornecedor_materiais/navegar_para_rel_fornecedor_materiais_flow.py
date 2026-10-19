from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_rel_fornecedor_materiais(page: Page) -> None:
    return acessar_universal(
        page,
        "Rel. Gerenciais - Fornecedores / Materiais Vendidos",
        caminho_v3=(
            "a:text-is('Almoxarifado')",
            "a:text-is('Relatórios')",
            "a:has-text('Rel. Gerenciais - Fornecedor/'), a:has-text('Rel.Ger.- Fornecedora/ Fornecedor/ Mat. Vendidos')"
        ),
        caminho_v4=(
            "div.module-text:text-is('Almoxarifado'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Relatórios'):visible",
            "div.menu-text:text-is('Fornecedor/Materiais Vendidos'):visible",
            "i.mdi.mdi-select-compare:visible",
        ),
    )
