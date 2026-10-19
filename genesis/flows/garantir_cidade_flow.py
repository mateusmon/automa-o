from loguru import logger
from playwright.sync_api import Page

from engine.execution_context import ExecutionContext
from navigation.navegar_para_cidade import acessar_cidade
from services.cidade_service import cidade_existe
from utils.espera import (
    aguardar_ajax_global,
    esperar_sucesso_ou_erro,
    preencher_campo,
)
from utils.versao_gen import escopo


def garantir_cidade(context: ExecutionContext) -> None:
    """
    Ensures cidade exists according to blueprint.
    """

    page = context.browser_manager.page
    blueprint = context.blueprint
    cidade_data = blueprint.get("cidade")
    
    if not cidade_data:
        logger.info("Nenhuma cidade definida no arquivo yaml. Ignorando fluxo.")
        return

    if not acessar_cidade(page):
        logger.warning("Menu 'Cidade' não disponível para este cliente. Pulando fluxo de cidade.")
        return

    nome = cidade_data["nome"]

    logger.info("Garantindo cidade de nome '{}'", nome)

    if cidade_existe(page, nome):
        logger.info("Cidade '{}' já existe. Nenhuma ação necesária.", nome)
        return

    logger.info("Cidade '{}' não encontrada. Criando...", nome)

    _criar_cidade(page, cidade_data)

    if not cidade_existe(page, nome):
        raise RuntimeError(
            f"Falha ao validar criação da cidade '{nome}'."
        )

    logger.success("Cidade '{}' criada com sucesso.", nome)


def _criar_cidade(page: Page, cidade_data: dict[str, str]) -> None:
    """
    Performs deterministic creation of cidade.
    Assumes prior existence check returned False.
    """

    if not acessar_cidade(page):
        logger.warning("Menu 'Cidade' não disponível para este cliente. Impossível criar cidade.")
        return

    ctx = escopo(page)

    ctx.locator("input[name='nmCidade']").fill(cidade_data["nome"])
    preencher_campo(ctx, "input[name='uf']", cidade_data["uf"])
    preencher_campo(ctx, "input[name='regiao']", cidade_data["regiao"])

    ctx.get_by_role("button", name="Confirmar").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)