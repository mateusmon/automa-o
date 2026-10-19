from playwright.sync_api import Page

from flows.shared.acessar_universal_flow import acessar_universal


def acessar_consulta(page: Page) -> None:
    acessar_universal(
        page,
        "Consulta Geral",
        caminho_v3=[
            "a:is(:has-text('Mobiliário'), :has-text('Patrimônio')) >> nth=0",
            "a:is(:has-text('Consulta Geral'), :has-text('Consulta')) >> nth=0",
        ],
        caminho_v4=[
            "div.module-text:text-is('Patrimônio'):visible",
        ],
    )
