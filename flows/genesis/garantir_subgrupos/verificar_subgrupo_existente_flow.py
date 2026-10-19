from typing import Any

from loguru import logger
from playwright.sync_api import Page

from flows.corporativo.material.cadastro_supply.navegar_para_supply_flow import (
    acessar_supply,
)
from utils.versao import escopo
from utils.waits import (
    aguardar_ajax_global,
    preencher_campo,
    select_tipo,
)


def verificar_subgrupo_existente(
    page: Page, grupos_data: list[dict[str, Any]]
) -> list[dict[str, Any]] | None:
    """Acessa a árvore de supply e identifica quais subgrupos da massa ainda não existem no sistema."""
    logger.info("Iniciando verificação de subgrupos existentes...")

    subgrupos_faltantes = []
    total_grupos = len(grupos_data)

    for idx_grupo, grupo in enumerate(grupos_data, start=1):
        nome_grupo = grupo.get("nome", f"Grupo {idx_grupo}")
        subgrupos = grupo.get("subgrupos", [])

        if not subgrupos:
            continue

        if isinstance(subgrupos, dict):
            subgrupos = [subgrupos]

        logger.info(
            "Verificando subgrupos do grupo '{}' ({}/{})",
            nome_grupo,
            idx_grupo,
            total_grupos,
        )

        for subgrupo in subgrupos:
            codigo = subgrupo["codigo"]
            nome = subgrupo["nome"]

            logger.info("Garantindo subgrupo código '{}' ({})", codigo, nome)

            if _checar_existencia_subgrupo_no_dom(page, codigo) is None:
                return None

            if _checar_existencia_subgrupo_no_dom(page, codigo):
                logger.info(
                    "Subgrupo '{}' (código {}) já existe. Nenhuma ação necessária.",
                    nome,
                    codigo,
                )
            else:
                logger.info(
                    "Subgrupo '{}' (código {}) não encontrado. Marcado para criação.",
                    nome,
                    codigo,
                )
                subgrupos_faltantes.append(subgrupo)

    return subgrupos_faltantes


def _checar_existencia_subgrupo_no_dom(page: Page, codigo_subgrupo: str) -> bool | None:
    """Abre o modal de consulta da árvore e verifica a presença do ícone de subgrupo visível."""
    if not acessar_supply(page):
        logger.info("Menu 'Supply' não disponível para este cliente.")
        return None

    ctx = escopo(page)

    # Abrir consulta de grupos/subgrupos
    ctx.locator("button[name='lookup-grupoDsExemplo']").click()
    aguardar_ajax_global(page)

    # Aguardar carregamento das opções de busca
    ctx.get_by_text("Procurar por:").wait_for(state="visible", timeout=30_000)
    ctx.locator("select[name='tpFil']").wait_for(state="visible")

    select_tipo(ctx, "tpFil", "SUBGRUPO")

    # Realizar busca pelo código
    preencher_campo(ctx, "input[name='filtro']", codigo_subgrupo)

    try:
        ctx.locator("img.x-tree-node-icon.icon-subgrupo-open").wait_for(
            state="visible", timeout=2_000
        )
        existe = True
    except Exception:
        existe = False

    # Fechar tela/modal de consulta
    ctx.locator("button[name='submitCancel']").click()
    aguardar_ajax_global(page)

    return existe
