from typing import Any

from loguru import logger
from playwright.sync_api import Page

from flows.corporativo.estrutura_organizacional.cadastro_ul.navegar_para_ul_flow import (
    acessar_ul,
)
from utils.versao import escopo, get_versao
from utils.waits import aguardar_ajax_global


def verificar_ul_existente(
    page: Page, uls_data: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Mapeia as ULs da massa e retorna as que ainda não estão cadastradas."""
    logger.info("Iniciando verificação de Unidades de Localização (UL) existentes...")

    uls_faltantes = []
    total = len(uls_data)

    for indice, ul in enumerate(uls_data, start=1):
        logger.info("Verificando Unidade de Localização {}/{}", indice, total)
        endereco_ul = ul["endereco"]
        sigla_ul = ul["sigla"]

        if _checar_existencia_ul_no_dom(page, endereco_ul):
            logger.info(
                "Unidade de localização '{}' já existe. Nenhuma ação necessária.",
                sigla_ul,
            )
        else:
            logger.info(
                "Unidade de localização '{}' não encontrada. Marcada para criação.",
                sigla_ul,
            )
            uls_faltantes.append(ul)

    return uls_faltantes


def _checar_existencia_ul_no_dom(page: Page, endereco: str) -> bool:
    """Acessa a tela de consulta e verifica se a UL existe no sistema."""
    acessar_ul(page)

    ctx = escopo(page)

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    ctx.locator("input[name='model-7']").fill(endereco)
    ctx.locator("button[name='lookup-model-7']").click()
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)

    if get_versao() >= 4:
        span_resultado = ctx.locator("span[name='searchResultSize']")
        span_resultado.wait_for(state="visible")
        count = int(span_resultado.inner_text().strip())
    else:
        ctx.wait_for_selector("table[name='paginationTable']", timeout=10_000)
        linhas = ctx.locator("table[name='paginationTable'] tbody.scrollBody tr")
        count = linhas.count()

    existe = False

    if count > 0:
        endereco_alvo = endereco.strip().lower()
        linhas = ctx.locator(
            "table[name='paginationTable'] tbody tr, table tbody tr"
        ).all()

        for linha in linhas:
            celulas = [
                td.inner_text().strip().lower() for td in linha.locator("td").all()
            ]

            if any(endereco_alvo in c for c in celulas):
                existe = True
                break

    cancel_btn = ctx.locator("button[name='submitCancel']").or_(
        ctx.get_by_role("button", name="Cancelar")
    )
    if cancel_btn.is_visible():
        cancel_btn.click()
        aguardar_ajax_global(page)

    return existe
