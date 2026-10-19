from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_parametro_baixa_frequencia(page: Page) -> bool:
    return acessar_universal(
        page,
        "Política de Compras - Parâmetros Baixa Frequência",
        caminho_v3=[
            "a:text-is('Almoxarifado')",
            "a:text-is('Gestão de Estoque')",
            ".menu-link > a[title='Política de Compras - Parâmetros Baixa Frequência']",
        ],
        caminho_v4=[
            "div.module-text:text-is('Almoxarifado'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Gestão de Estoque'):visible",
            "div.menu-text:text-is('Politica de Compras'):visible",
            "div.menu-text:text-is('Parâmetros Baixa Frequência'):visible",
            "i.mdi.mdi-select-compare:visible",
        ],
        opcional=True,
    )
