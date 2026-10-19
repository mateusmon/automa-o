from loguru import logger
from playwright.sync_api import Page

from engine.execution_context import ExecutionContext
from navigation.navegar_para_centro_custo import acessar_centro_custo
from services.centro_custo_service import centro_custo_existe
from utils.espera import (
    aguardar_ajax_global,
    esperar_sucesso_ou_erro,
)
from utils.versao_gen import escopo


def garantir_centro_custo(context: ExecutionContext) -> None:
    """
    Ensures centro de custo exists according to blueprint.
    """

    page = context.browser_manager.page
    blueprint = context.blueprint
    centro_custo_data = blueprint.get("centro_custo")

    if not centro_custo_data:
        logger.info("Nenhum centro de custos definido no arquivo yaml. Ignorando fluxo.")
        return

    if not acessar_centro_custo(page):
        logger.warning("Menu 'CC - Centro de Custos' não disponível para este cliente. Pulando fluxo de centro de custos.")
        return

    nome = centro_custo_data["nome"]

    logger.info("Garantindo centro de custos '{}'", nome)

    if centro_custo_existe(page, nome):
        logger.info("Centro de custos '{}' já existe. Nenhuma ação necesária.", nome)
        return

    logger.info("Centro de custos '{}' não encontrado. Criando...", nome)

    _criar_centro_custo(page, centro_custo_data)

    if not centro_custo_existe(page, nome):
        raise RuntimeError(
            f"Falha ao validar criação da centro de custos '{nome}'."
        )

    logger.success("Centro de custos '{}' criado com sucesso.", nome)


def _criar_centro_custo(page: Page, centro_custo_data: dict[str, str]) -> None:
    """
    Performs deterministic creation of centro de custo.
    Assumes prior existence check returned False.
    """

    if not acessar_centro_custo(page):
        logger.warning("Menu 'CC - Centro de Custos' não disponível para este cliente. Impossível criar centro de custos.")
        return

    ctx = escopo(page)

    ctx.locator("input[name='nmCentroCusto']").fill(centro_custo_data["nome"])

    ctx.get_by_role("button", name="Confirmar").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)