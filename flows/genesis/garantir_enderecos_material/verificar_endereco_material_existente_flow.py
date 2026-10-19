from typing import Any

from loguru import logger
from playwright.sync_api import Page

from flows.almoxarifado.auxiliares.endereco_estoque.navegar_para_endereco_estoque_flow import (
    acessar_endereco_estoque,
)
from utils.versao import escopo, get_versao
from utils.waits import aguardar_ajax_global


def verificar_endereco_material_existente(
    page: Page,
    almoxarifados_data: list[dict[str, Any]],
    enderecos_data: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Identifica quais combinações de (almoxarifado + endereço) ainda não existem no sistema."""
    logger.info("Iniciando verificação de endereços de material existentes...")

    total_almoxarifados = len(almoxarifados_data)
    total_enderecos = len(enderecos_data)

    logger.info(
        "Foi encontrado um total de {} almoxarifados e {} endereços por almoxarifado.",
        total_almoxarifados,
        total_enderecos,
    )

    enderecos_faltantes = []

    for idx_alm, almoxarifado in enumerate(almoxarifados_data, start=1):
        sigla_almoxarifado = almoxarifado["sigla"]
        logger.info(
            "Almoxarifado {}/{} ({})", idx_alm, total_almoxarifados, sigla_almoxarifado
        )

        for idx_end, endereco in enumerate(enderecos_data, start=1):
            descricao_endereco = endereco["descricao"]
            logger.info(
                "Endereço {}/{} - Garantindo descrição '{}'",
                idx_end,
                total_enderecos,
                descricao_endereco,
            )

            if _checar_existencia_endereco_no_dom(
                page, descricao_endereco, sigla_almoxarifado
            ):
                logger.info(
                    "Endereço de material '{}' no almoxarifado '{}' já existe. Nenhuma ação necessária.",
                    descricao_endereco,
                    sigla_almoxarifado,
                )
            else:
                logger.info(
                    "Endereço de material '{}' no almoxarifado '{}' não encontrado. Marcado para criação.",
                    descricao_endereco,
                    sigla_almoxarifado,
                )
                enderecos_faltantes.append(
                    {"almoxarifado": almoxarifado, "endereco": endereco}
                )

    return enderecos_faltantes


def _checar_existencia_endereco_no_dom(
    page: Page, descricao_endereco: str, sigla_almoxarifado: str
) -> bool:
    """Abre a consulta de Endereço de Estoque e verifica a quantidade de registros encontrados."""
    acessar_endereco_estoque(page)
    ctx = escopo(page)

    ctx.get_by_role("button", name="Consulta", exact=True).click()
    aguardar_ajax_global(page)

    # Filtro por Almoxarifado
    ctx.locator("input[name='model-1']").fill(sigla_almoxarifado)
    ctx.locator("button[name='lookup-model-1']").click()
    aguardar_ajax_global(page)

    # Filtro por Descrição do Endereço
    ctx.locator("input[name='model-3']").fill(descricao_endereco)
    ctx.get_by_title("Consultar novo registro").click()
    aguardar_ajax_global(page)

    if get_versao() >= 4:
        span_resultado = ctx.locator("span[name='searchResultSize']")
        span_resultado.wait_for(state="visible")
        count = int(span_resultado.inner_text().strip())
    else:
        ctx.wait_for_selector("table[name='paginationTable']", timeout=10_000)
        linhas = ctx.locator("table[name='paginationTable'] tbody.scrollBody tr")
        count = linhas.count()

    ctx.get_by_role("button", name="Cancelar").click()
    aguardar_ajax_global(page)

    if count == 0:
        return False

    if count == 1:
        return True

    raise RuntimeError(
        f"Múltiplos endereços de material detectados para '{descricao_endereco}'. Total: {count}"
    )
