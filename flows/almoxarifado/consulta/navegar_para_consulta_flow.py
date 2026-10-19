from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_consulta(page: Page) -> None:
    acessar_universal(
        page,
        "Consulta de Material",
        caminho_v3=[
                "a:text-is('Almoxarifado')",
                ".menu-link > a[url*='ConsultaMaterialEditGateway']"
            ],
        caminho_v4=[
                "div.module-text:has-text('Almoxarifado')"
            ]
        )