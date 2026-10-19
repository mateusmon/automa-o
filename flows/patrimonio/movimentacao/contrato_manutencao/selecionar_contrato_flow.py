from playwright.sync_api import Page

from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao


def selecionar_contrato(page: Page, ug: dict[str, str]) -> bool:

    ha_contratos = selecionar_movimentacao(page, ug["codigo"])
    return ha_contratos
