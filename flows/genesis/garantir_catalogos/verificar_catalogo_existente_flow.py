from typing import Any

from loguru import logger
from playwright.sync_api import Page

from flows.almoxarifado.auxiliares.catalogo_restrito.navegar_para_catalogo_restrito_flow import (
    acessar_catalogo_restrito,
)
from utils.versao import escopo, get_versao
from utils.waits import aguardar_ajax_global


def verificar_catalogo_existente(
    page: Page,
    almoxarifados_data: list[dict[str, Any]],
    catalogo_data: dict[str, Any],
) -> list[dict[str, Any]]:
    """Identifica em quais almoxarifados o catálogo informado ainda não foi criado."""
    logger.info("Iniciando verificação de catálogos existentes...")

    catalogos_faltantes = []
    total = len(almoxarifados_data)
    nome_catalogo = catalogo_data["nome"]

    for atual, almoxarifado in enumerate(almoxarifados_data, start=1):
        sigla_almoxarifado = almoxarifado["sigla"]
        logger.info(
            "Almoxarifado {}/{} - Garantindo catálogo no Almoxarifado'{}'",
            atual,
            total,
            sigla_almoxarifado,
        )

        if _checar_existencia_catalogo_no_dom(page, sigla_almoxarifado, nome_catalogo):
            logger.info(
                "Catálogo '{}' já existe para o almoxarifado '{}'. Nenhuma ação necessária.",
                nome_catalogo,
                sigla_almoxarifado,
            )
        else:
            logger.info(
                "Catálogo '{}' não encontrado para o almoxarifado '{}'. Marcado para criação.",
                nome_catalogo,
                sigla_almoxarifado,
            )
            catalogos_faltantes.append(almoxarifado)

    return catalogos_faltantes


def _checar_existencia_catalogo_no_dom(
    page: Page, sigla_almox: str, nome_catalogo: str
) -> bool:
    """Acessa a consulta de catálogos e verifica a existência do registro."""
    acessar_catalogo_restrito(page)

    ctx = escopo(page)

    ctx.get_by_role("button", name="Consulta", exact=True).click()
    aguardar_ajax_global(page)

    ctx.locator("input[name='model-1']").fill(sigla_almox)
    if get_versao() < 4:
        ctx.locator("button[name='lookup-model-1']").click()
        aguardar_ajax_global(page)

    ctx.locator("input[name='model-3']").fill(nome_catalogo)
    ctx.locator("button[name='submitSearch']").or_(
        ctx.get_by_title("Consultar novo registro")
    ).first.click()
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
        catalogo_alvo = nome_catalogo.strip().lower()
        linhas = ctx.locator(
            "table[name='paginationTable'] tbody tr, table tbody tr"
        ).all()

        for linha in linhas:
            celulas = [
                td.inner_text().strip().lower() for td in linha.locator("td").all()
            ]

            if any(catalogo_alvo in c for c in celulas):
                existe = True
                break

    cancel_btn = ctx.locator("button[name='submitCancel']").or_(
        ctx.get_by_role("button", name="Cancelar")
    )
    if cancel_btn.is_visible():
        cancel_btn.click()
        aguardar_ajax_global(page)

    return existe
