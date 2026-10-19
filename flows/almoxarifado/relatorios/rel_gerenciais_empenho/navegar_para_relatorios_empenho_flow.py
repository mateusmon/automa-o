from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal

# O caminho_v3 é apenas por ser obrigatório na função acessar_universal, visto que esse teste é somente para v4.
def acessar_relatorios_empenho(page: Page) -> None:
    return acessar_universal(
        page,
        "Rel. Gerenciais - Materiais Vendidos/Fornecedores",
        caminho_v3=(
            "a:text-is('Almoxarifado')",
            "a:text-is('Relatórios')",
            ".menu-link > a[title='Rel. Gerenciais - Empenho']",
        ),
        caminho_v4=(
            "div.module-text:text-is('Almoxarifado'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Relatórios'):visible",
            "div.menu-text:text-is('Empenho'):visible",
            "i.mdi.mdi-select-compare:visible",
        ),
    )
