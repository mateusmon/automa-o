from loguru import logger
from playwright.sync_api import Page

from engine.execution_context import ExecutionContext
from navigation.navegar_para_ua import acessar_ua
from services.ua_service import ua_existe
from utils.espera import (
    aguardar_ajax_global,
    esperar_sucesso_ou_erro,
    preencher_campo,
)
from utils.versao_gen import escopo


def garantir_ua(context: ExecutionContext) -> None:
    """
    Ensures ua exists according to blueprint.
    """

    page = context.browser_manager.page
    blueprint = context.blueprint
    ua_data = blueprint.get("unidade_administrativa")
    sigla_ug = context.runtime_config["unidade_gestora"]["sigla"]

    if not ua_data:
        logger.info("Nenhuma UA definida no arquivo yaml. Ignorando fluxo.")
        return

    if not acessar_ua(page):
        logger.warning("Menu 'UA - Unidade Administrativa' não disponível para este cliente. Pulando fluxo de UA.")
        return

    sigla = ua_data["sigla"]

    logger.info("Garantindo UA sigla '{}'", sigla)

    if ua_existe(page, sigla):
        logger.info("UA '{}' já existe. Nenhuma ação necesária.", sigla)
        return

    logger.info("UA '{}' não encontrado. Criando...", sigla)

    _criar_ua(page, ua_data, sigla_ug)

    if not ua_existe(page, sigla):
        raise RuntimeError(
            f"Falha ao validar criação de UA '{sigla}'."
        )

    logger.success("UA '{}' criada com sucesso.", sigla)


def _criar_ua(page: Page, ua_data: dict, sigla_ug: str) -> None:
    """
    Performs deterministic creation of unidade_administrativa.
    Assumes prior existence check returned False.
    """
    sigla = ua_data["sigla"]
    nome = ua_data["nome"]
    responsavel = ua_data["responsavel"]
    nome_responsavel = responsavel["nome"]
    funcao_responsavel = responsavel["funcao"]

    if not acessar_ua(page):
        logger.warning("Menu 'UA - Unidade Administrativa' não disponível para este cliente. Impossível criar UA.")
        return

    ctx = escopo(page)

    ctx.locator("input[name='sgUa']").fill(sigla)
    ctx.locator("input[name='nmUa']").fill(nome)

    if ctx.locator("input[name='ug']").is_enabled():
        preencher_campo(ctx, "input[name='ug']", sigla_ug)

    ctx.get_by_role("button", name="Responsáveis").click()
    aguardar_ajax_global(page)

    preencher_campo(ctx, "input[name='funcionario-1-2']", nome_responsavel)
    preencher_campo(ctx, "input[name='tipoFuncao-1-3']", funcao_responsavel)

    ctx.locator("input[name='hierarquia-1-5']").check()
    ctx.get_by_role("button", name="Confirmar").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)