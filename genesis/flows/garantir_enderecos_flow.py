from loguru import logger
from playwright.sync_api import Page

from engine.execution_context import ExecutionContext
from navigation.navegar_para_endereco import acessar_endereco
from services.endereco_service import endereco_existe
from utils.espera import (
    aguardar_ajax_global,
    esperar_sucesso_ou_erro,
    preencher_campo,
)
from utils.versao_gen import escopo


def garantir_enderecos(context: ExecutionContext) -> None:
    """
    Ensures enderecos exists according to blueprint.
    """

    page = context.browser_manager.page
    blueprint = context.blueprint
    enderecos_data = blueprint.get("enderecos")

    if not enderecos_data:
        logger.info("Nenhum endereço definido no arquivo yaml. Ignorando fluxo.")
        return

    if not acessar_endereco(page):
        logger.warning("Menu 'Endereço' não disponível para este cliente. Pulando fluxo de endereços.")
        return

    total = len(enderecos_data)

    logger.info("Foi encontrado um total de {} endereços no arquivo yaml.", total)

    for atual, endereco in enumerate(enderecos_data, start=1):
        logger.info("Endereço {}/{}", atual, total)

        nome_endereco = endereco["nome"]

        logger.info("Garantindo endereço nome '{}'", nome_endereco)

        if endereco_existe(page, nome_endereco):
            logger.info("Endereço '{}' já existe. Nenhuma ação necesária.", nome_endereco)
            continue

        logger.info("Endereço '{}' não encontrado. Criando...", nome_endereco)

        _criar_endereco(page, endereco)

        if not endereco_existe(page, nome_endereco):
            raise RuntimeError(
                f"Falha ao validar criação de endereço '{nome_endereco}'."
            )

        logger.success("Endereço '{}' criado com sucesso.", nome_endereco)


def _criar_endereco(page: Page, endereco_data: dict) -> None:
    """
    Performs deterministic creation of endereco.
    Assumes prior existence check returned False.
    """
    nome_endereco = endereco_data["nome"]
    instalacao_endereco = endereco_data["instalacao"]

    if not acessar_endereco(page):
        logger.warning("Menu 'Endereço' não disponível para este cliente. Impossível criar endereço.")
        return

    ctx = escopo(page)

    # Clica no botão "Novo" se já houver dados preenchidos na tela
    if ctx.locator("input[name='instalacao']").input_value() != "":
        ctx.get_by_role("button", name="Novo").click()
        aguardar_ajax_global(page)

    ctx.locator("input[name='nmLocal']").fill(nome_endereco)

    preencher_campo(ctx, "input[name='instalacao']", instalacao_endereco)

    ctx.get_by_role("button", name="Confirmar").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)