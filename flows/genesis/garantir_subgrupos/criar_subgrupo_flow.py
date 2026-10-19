from typing import Any

from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import (
    aguardar_ajax_global,
    esperar_sucesso_ou_erro,
    preencher_campo,
)


def criar_subgrupo(page: Page, subgrupos_faltantes: list[dict[str, Any]]) -> None:
    """Realiza o cadastro determinístico de todos os subgrupos pendentes."""
    if not subgrupos_faltantes:
        return

    logger.info(f"Iniciando criação de {len(subgrupos_faltantes)} subgrupo(s)...")

    for subgrupo in subgrupos_faltantes:
        logger.info(
            "Criando subgrupo '{}' (código: {})...",
            subgrupo["nome"],
            subgrupo["codigo"],
        )
        _preencher_formulario_subgrupo(page, subgrupo)

    logger.info("Criação de subgrupos concluída.")


def _preencher_formulario_subgrupo(page: Page, subgrupo_data: dict[str, Any]) -> None:
    """Preenche e confirma o cadastro de um único subgrupo no modal da árvore."""
    codigo_subgrupo = subgrupo_data["codigo"]
    nome_subgrupo = subgrupo_data["nome"]

    ctx = escopo(page)

    # Selecionar o grupo pai pela árvore
    ctx.locator("button[name='lookup-grupoDsExemplo']").click()
    aguardar_ajax_global(page)

    # Filtra usando os 2 primeiros dígitos (código do Grupo Pai)
    preencher_campo(ctx, "input[name='filtro']", codigo_subgrupo[:2])

    ctx.locator("img.x-tree-node-icon.icon-grupo-open").dblclick()
    aguardar_ajax_global(page)

    # Ações de adição de linha na interface
    ctx.locator("button[name='submitAddLine1']").click()
    aguardar_ajax_global(page)

    ctx.locator("button[name='submitAddLine2']").click()
    aguardar_ajax_global(page)

    # Preenchimento do subgrupo e material modelo
    ctx.locator("input[name='subgrupoCdExemplo']").fill(codigo_subgrupo)
    ctx.locator("input[name='subgrupoDsExemplo']").fill(nome_subgrupo)
    ctx.locator("input[name='materialDsExemplo']").fill("MATERIAL AUTOMATIZADO")

    # Confirmar operação
    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)
