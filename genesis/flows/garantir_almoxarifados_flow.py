from loguru import logger
from playwright.sync_api import Page

from engine.execution_context import ExecutionContext
from navigation.navegar_para_almoxarifado import acessar_almoxarifado
from services.almoxarifado_service import almoxarifado_existe
from utils.espera import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo
from utils.versao_gen import escopo


def garantir_almoxarifados(context: ExecutionContext) -> None:
    """
    Ensures almoxarifados exists according to blueprint.
    """

    page = context.browser_manager.page
    blueprint = context.blueprint
    almoxarifados_data = blueprint.get("almoxarifados")
    sigla_ug = context.runtime_config["unidade_gestora"]["sigla"]

    if not almoxarifados_data:
        logger.info("Nenhum almoxarifado definido no arquivo yaml. Ignorando fluxo.")
        return

    if not acessar_almoxarifado(page):
        logger.error("Menu 'Almoxarifado' não disponível para este cliente.")
        return

    total = len(almoxarifados_data)

    logger.info("Foi encontrado um total de {} almoxarifados no arquivo yaml.", total)

    for atual, almoxarifado in enumerate(almoxarifados_data, start=1):

        logger.info("Almoxarifado {}/{}", atual, total)

        nome_almoxarifado = almoxarifado["nome"]
        sigla_almoxarifado = almoxarifado["sigla"]

        logger.info("Garantindo almoxarifado nome '{}'", nome_almoxarifado)

        if almoxarifado_existe(page, sigla_almoxarifado):
            logger.info("Almoxarifado '{}' já existe. Nenhuma ação necesária.", nome_almoxarifado)
            continue
        
        logger.info("Almoxarifado '{}' não encontrado. Criando...", nome_almoxarifado)
        
        _criar_almoxarifado(page, almoxarifado, sigla_ug)

        # --- Post-creation validation ---
        if not almoxarifado_existe(page, sigla_almoxarifado):
            raise RuntimeError(
                f"Falha ao validar criação de almoxarifado '{nome_almoxarifado}'."
            )
        
        logger.success("Almoxarifado '{}' criado com sucesso.", nome_almoxarifado)


def _criar_almoxarifado(page: Page, almoxarifado_data: dict, sigla_ug: str) -> None:
    """
    Performs deterministic creation of almoxarifado.
    Assumes prior existence check returned False.
    """
    nome_almoxarifado = almoxarifado_data["nome"]
    sigla_almoxarifado = almoxarifado_data["sigla"]

    # Navigation
    if not acessar_almoxarifado(page):
        logger.error("Menu 'Almoxarifado' não disponível para este cliente.")
        return

    ctx = escopo(page)

    if ctx.locator("input[name='cdAlmoxarifado']").input_value() != "":
        ctx.get_by_role("button", name="Novo").click()
        aguardar_ajax_global(page)
    
    ctx.locator("input[name='dsAlmoxarifado']").fill(nome_almoxarifado)
    ctx.locator("input[name='sgAlmoxarifado']").fill(sigla_almoxarifado)

    ctx.locator("input[name='inControleFin'][value='S']").check()
    aguardar_ajax_global(page)
    
    preencher_campo(ctx, "input[name='cdUg']", sigla_ug)

    ctx.get_by_role("button", name="Confirmar").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)