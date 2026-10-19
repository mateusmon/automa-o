from loguru import logger
from playwright.sync_api import Page

from engine.execution_context import ExecutionContext
from navigation.navegar_para_ur import acessar_ur
from services.ur_service import ur_existe
from utils.espera import (
    aguardar_ajax_global,
    esperar_sucesso_ou_erro,
    preencher_campo,
)
from utils.versao_gen import escopo


def garantir_urs(context: ExecutionContext) -> None:
    """
    Ensures urs exists according to blueprint.
    """

    page = context.browser_manager.page
    blueprint = context.blueprint
    urs_data = blueprint.get("unidades_requisicao")

    if not urs_data:
        logger.info("Nenhuma unidade de requisição definida no arquivo yaml. Ignorando fluxo.")
        return

    if not acessar_ur(page):
        logger.warning("Menu 'UR - Unidade de Requisição' não disponível para este cliente. Pulando fluxo de unidades de requisição.")
        return

    total = len(urs_data)

    logger.info("Foi encontrado um total de {} unidades de requisição no arquivo yaml.", total)

    for atual, ur in enumerate(urs_data, start=1):
        logger.info("Unidade de requisição {}/{}", atual, total)

        nome_ur = ur["nome"]

        logger.info("Garantindo unidade de requisição nome '{}'", nome_ur)

        if ur_existe(page, nome_ur):
            logger.info("Unidade de requisição '{}' já existe. Nenhuma ação necesária.", nome_ur)
            continue

        logger.info("Unidade de requisição '{}' não encontrada. Criando...", nome_ur)

        _criar_ur(page, ur)

        if not ur_existe(page, nome_ur):
            raise RuntimeError(
                f"Falha ao validar criação de unidade de requisição '{nome_ur}'."
            )

        logger.success("Unidade de requisição '{}' criada com sucesso.", nome_ur)


def _criar_ur(page: Page, ur_data: dict) -> None:
    """
    Performs deterministic creation of ur.
    Assumes prior existence check returned False.
    """
    sigla_ua = ur_data["sigla_ua"]
    nome_ur = ur_data["nome"]
    endereco_ur = ur_data["endereco"]

    if not acessar_ur(page):
        logger.warning("Menu 'UR - Unidade de Requisição' não disponível para este cliente. Impossível criar unidade de requisição.")
        return

    ctx = escopo(page)

    # Clicando em novo porque a página continua com os dados depois de confirmar
    if ctx.locator("input[name='cdUg']").input_value() != "":
        ctx.get_by_role("button", name="Novo").click()
        aguardar_ajax_global(page)

    preencher_campo(ctx, "input[name='cdUa']", sigla_ua)

    if ctx.locator("input[name='cdCentroCusto']").is_enabled():
        preencher_campo(ctx, "input[name='cdCentroCusto']", ur_data["centro_custo"])

    ctx.locator("input[name='nmUr']").fill(nome_ur)

    preencher_campo(ctx, "input[name='cdLocal']", endereco_ur)

    ctx.get_by_role("button", name="Confirmar").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)