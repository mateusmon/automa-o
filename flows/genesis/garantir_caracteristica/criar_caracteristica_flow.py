from loguru import logger
from playwright.sync_api import Page, expect

from utils.versao import escopo
from utils.waits import (
    aguardar_ajax_global,
    esperar_sucesso_ou_erro,
)


def criar_caracteristica(page: Page) -> None:
    """Associa uma característica genérica ao Bem cadastrado."""
    logger.info("Iniciando fluxo de associação de característica ao Bem...")
    _preencher_formulario_caracteristica(page)
    logger.info("Associação de característica concluída.")


def _preencher_formulario_caracteristica(page: Page) -> None:
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
