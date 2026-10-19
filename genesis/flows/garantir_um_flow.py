from loguru import logger
from playwright.sync_api import Page

from engine.execution_context import ExecutionContext
from navigation.navegar_para_unidade_medida import acessar_unidade_medida
from services.um_service import um_existe
from utils.espera import (
    aguardar_ajax_global,
    esperar_sucesso_ou_erro,
)
from utils.versao_gen import escopo


def garantir_um(context: ExecutionContext) -> None:
    """
    Ensures unidade de medida exists according to blueprint.
    """
    page = context.browser_manager.page
    blueprint = context.blueprint
    um_data = blueprint.get("unidade_medida")

    if not um_data:
        logger.info("Nenhum unidade de medida definida no arquivo yaml. Ignorando fluxo.")
        return

    if not acessar_unidade_medida(page):
        logger.error("Menu 'Unidade de Medida' não disponível para este cliente.")
        return

    sigla = um_data["sigla"]
    logger.info("Garantindo unidade de medida sigla '{}'", sigla)

    if um_existe(page, sigla):
        logger.info("Unidade de medida '{}' já existe. Nenhuma ação necessária.", sigla)
        return

    logger.info("Unidade de medida '{}' não encontrada. Criando...", sigla)
    _criar_um(page, um_data)

    # --- Post-creation validation ---
    if not um_existe(page, sigla):
        raise RuntimeError(
            f"Falha ao validar criação da unidade de medida '{sigla}'."
        )

    logger.success("Unidade de medida '{}' criada com sucesso.", sigla)


def _criar_um(page: Page, um_data: dict) -> None:
    """
    Performs deterministic creation of um.
    Assumes prior existence check returned False.
    """
    descricao = um_data["descricao"]
    sigla = um_data["sigla"]

    if not acessar_unidade_medida(page):
        logger.error("Menu 'Unidade de Medida' não disponível para este cliente.")
        return

    ctx = escopo(page)
    ctx.locator("button[name='submitFinish']").wait_for(state="visible")

    if ctx.locator("input[name='sgUm']").input_value() != "":
        ctx.get_by_role("button", name="Novo").click()
        aguardar_ajax_global(page)

    ctx.locator("input[name='dsUm']").fill(descricao)
    ctx.locator("input[name='sgUm']").fill(sigla)

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)
