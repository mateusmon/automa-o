from loguru import logger
from playwright.sync_api import Page

from engine.execution_context import ExecutionContext
from navigation.navegar_para_endereco_material import acessar_endereco_material
from services.endereco_material_service import endereco_existe
from utils.espera import (
    aguardar_ajax_global,
    esperar_pagina_carregar,
    esperar_sucesso_ou_erro,
    preencher_campo,
)
from utils.versao_gen import escopo, get_versao


def garantir_endereco_material(context: ExecutionContext) -> None:
    """
    Ensures endereco_material exists according to blueprint.
    """
    page = context.browser_manager.page
    blueprint = context.blueprint
    almoxarifado_data = blueprint.get("almoxarifados")
    endereco_material_data = blueprint.get("enderecos_material")

    if not almoxarifado_data:
        logger.info("Nenhum almoxarifado definido no arquivo yaml. Ignorando fluxo.")
        return

    if not endereco_material_data:
        logger.info("Nenhum endereço de material definido no arquivo yaml. Ignorando fluxo.")
        return

    if not acessar_endereco_material(page):
        logger.error("Menu 'Endereço de Estoque' não disponível para este cliente.")
        return

    total_almoxarifado = len(almoxarifado_data)
    total_endereco = len(endereco_material_data)

    logger.info("Foi encontrado um total de {} almoxarifados no arquivo yaml.", total_almoxarifado)
    logger.info("Total de endereços por almoxarifado: {}", total_endereco)

    for indice, almoxarifado in enumerate(almoxarifado_data, start=1):
        sigla_almoxarifado = almoxarifado["sigla"]
        logger.info("Almoxarifado {}/{}", indice, total_almoxarifado)

        for indice_endereco, endereco in enumerate(endereco_material_data, start=1):
            descricao_endereco = endereco["descricao"]
            logger.info("Endereço {}/{}", indice_endereco, total_endereco)
            logger.info("Garantindo endereço de material de descrição '{}'.", descricao_endereco)

            if endereco_existe(page, descricao_endereco, sigla_almoxarifado):
                logger.info("Endereço de material '{}' já existe. Nenhuma ação necesária.", descricao_endereco)
                continue

            logger.info("Endereço de material '{}' não encontrado. Criando...", descricao_endereco)
            _criar_endereco(page, endereco, almoxarifado)

            # --- Post-creation validation ---
            if not endereco_existe(page, descricao_endereco, sigla_almoxarifado):
                raise RuntimeError(
                    f"Falha ao validar criação da endereço de material '{descricao_endereco}'."
                )

            logger.success("Endereço de material '{}' criada com sucesso.", descricao_endereco)


def _criar_endereco(page: Page, endereco: dict, almoxarifado_data: dict) -> None:
    """
    Performs deterministic creation of endereco.
    Assumes prior existence check returned False.
    """
    codigo_endereco = endereco["codigo"]
    descricao_endereco = endereco["descricao"]
    sigla_endereco = endereco["sigla"]
    sigla_almoxarifado = almoxarifado_data["sigla"]

    if not acessar_endereco_material(page):
        logger.error("Menu 'Endereço de Estoque' não disponível para este cliente.")
        return

    ctx = escopo(page)

    if ctx.locator("input[name='almoxarifado']").input_value() != "":
        ctx.get_by_role("button", name="Novo").click()
        aguardar_ajax_global(page)

    preencher_campo(ctx, "input[name='almoxarifado']", sigla_almoxarifado)

    codigo_input = ctx.locator("input[name='cdEndereco']")
    if codigo_input.is_enabled():
        codigo_input.fill(codigo_endereco)
        
    ctx.locator("input[name='dsEnderecoEst']").fill(descricao_endereco)
    ctx.locator("input[name='sgEnderecoEst']").fill(sigla_endereco)

    ctx.locator("input[name='idUltNivel']").check()

    ctx.get_by_role("button", name="Confirmar").click()
    
    if get_versao() >= 4:
        aguardar_ajax_global(page)
        esperar_sucesso_ou_erro(ctx)
    else:
        esperar_pagina_carregar(page)
        esperar_sucesso_ou_erro(page)
