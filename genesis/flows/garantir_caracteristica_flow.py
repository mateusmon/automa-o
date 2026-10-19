from loguru import logger
from playwright.sync_api import Page, expect

from engine.execution_context import ExecutionContext
from navigation.navegar_para_bem import acessar_bem, heading_bem_visivel
from services.caracteristica_service import possui_caracteristica
from utils.espera import (
    aguardar_ajax_global,
    esperar_sucesso_ou_erro,
)
from utils.versao_gen import escopo


def garantir_caracteristica(context: ExecutionContext) -> None:
    page = context.browser_manager.page

    logger.info("Verificando se tem alguma característica relacionada ao bem.")
    if possui_caracteristica(page):
        logger.info("Já exite uma característica relacionada ao bem.")
        return
    
    logger.info("Garantindo alguma característica relacionada ao bem.")
    _adicionar_caracteristica(page)

    # --- Post-creation validation ---
    if not possui_caracteristica(page):
        raise RuntimeError(
            "Falha ao validar relacionamento da característica com o bem."
        )
    
    logger.success("Característica relacionada com sucesso.")


def _adicionar_caracteristica(page: Page):
    """
    Performs deterministic creation of caracteristica.
    Assumes prior existence check returned False.
    """
    section = page.locator('caption .title', has_text="Características")
    if not (heading_bem_visivel(page) and section.is_visible()):
        acessar_bem(page)

    ctx = escopo(page)
    ctx.locator('button[name="lookup-caracteristicas-Nome-1-3"]').click()
    aguardar_ajax_global(page)
    ctx.locator('button[name="submitSearch"]').click()
    aguardar_ajax_global(page)
    expect(ctx.locator('td[name="cell-1-2"]')).not_to_be_empty()
    ctx.locator('button[name="submitUse"][usefield="cell-1-1"]').click()
    aguardar_ajax_global(page)
    ctx.locator('button[name="submitFinish"]').click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)
