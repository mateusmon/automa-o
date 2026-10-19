from loguru import logger
from playwright.sync_api import Page

from navigation.navegar_para_subgrupo import acessar_subgrupo
from utils.espera import (
    aguardar_ajax_global,
    preencher_campo,
    select_tipo,
)
from utils.versao_gen import escopo


def subgrupo_existe(page: Page, nome_subgrupo: str) -> bool:
    """
    Returns True if subgrupo exists in Supply tree, False otherwise.
    """
    # Navigation
    if not acessar_subgrupo(page):
        logger.warning("Menu 'Supply' não disponível para este cliente. Ignorando verificação de subgrupo.")
        return False

    ctx = escopo(page)

    # Open consultation page
    ctx.locator("button[name='lookup-grupoDsExemplo']").click()
    aguardar_ajax_global(page)

    # Esperando a página aparecer
    ctx.get_by_text("Procurar por:").wait_for(state="visible", timeout=30_000)
    ctx.locator("select[name='tpFil']").wait_for(state="visible")

    select_tipo(ctx, "tpFil", "SUBGRUPO")

    # Search
    preencher_campo(ctx, "input[name='filtro']", nome_subgrupo)

    try:
        ctx.locator("img.x-tree-node-icon.icon-subgrupo-open").wait_for(state="visible", timeout=1_000)
        existe = True
    except Exception:
        existe = False

    ctx.locator("button[name='submitCancel']").click()
    aguardar_ajax_global(page)
    return existe
