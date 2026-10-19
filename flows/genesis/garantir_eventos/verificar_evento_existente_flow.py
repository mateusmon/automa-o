from typing import Any

from loguru import logger
from playwright.sync_api import Page

from flows.almoxarifado.gestao_de_compras.evento.navegar_para_evento_flow import (
    acessar_evento,
)
from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def verificar_evento_existente(page: Page, evento_data: dict[str, Any]) -> bool:
    """Verifica se o evento especificado no YAML já se encontra cadastrado."""
    nome_evento = evento_data["nome"]
    logger.info("Iniciando verificação do evento '{}'...", nome_evento)
    return _checar_existencia_evento_no_dom(page, nome_evento)


def _checar_existencia_evento_no_dom(page: Page, nome: str) -> bool:
    """Acessa a tela de eventos e realiza a busca pelo nome exato no sistema."""
    acessar_evento(page)

    ctx = escopo(page)

    ctx.get_by_role("button", name="Consulta", exact=True).click()
    aguardar_ajax_global(page)

    ctx.locator("#model-3").fill(nome)  # Descrição
    ctx.get_by_title("Consultar novo registro").click()
    aguardar_ajax_global(page)

    span_resultado = ctx.locator("span[name='searchResultSize']")
    span_resultado.wait_for(state="visible")
    count = int(span_resultado.inner_text().strip())

    existe = False

    if count > 0:
        nome_alvo = nome.strip().lower()
        linhas = ctx.locator("table tbody tr").all()

        for linha in linhas:
            celulas = [
                td.inner_text().strip().lower() for td in linha.locator("td").all()
            ]

            if nome_alvo in celulas:
                existe = True
                break

    ctx.get_by_role("button", name="Cancelar").click()
    aguardar_ajax_global(page)

    return existe
