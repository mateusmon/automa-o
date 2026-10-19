from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_relatorio_saldo_previsao_consumo(page: Page) -> bool:
    return acessar_universal(
        page,
        "Relatório Saldo de Previsão de Consumo",
        caminho_v3=(
            "a:text-is('Almoxarifado')",
            "a:text-is('Relatórios')",
            ".menu-link > a[title='Relatório Saldo de Previsão de Consumo']",
        ),
        caminho_v4=(
            "div.module-text:text-is('Almoxarifado'):visible",
            "i.mdi.mdi-select-compare:visible",
            "div.menu-text:text-is('Relatórios'):visible",
            "div.menu-text:text-is('Saldo de Previsão de Consumo'):visible",
            "i.mdi.mdi-select-compare:visible",
        ),
        opcional=True,
    )
