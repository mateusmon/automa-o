from loguru import logger
from playwright.sync_api import Page

from engine.execution_context import ExecutionContext
from navigation.navegar_para_enderecamento import acessar_enderecamento
from services.enderecamento_material_service import (
    enderecamento_existe,
    material_ja_selecionado,
)
from utils.espera import (
    aguardar_ajax_global,
    esperar_sucesso_ou_erro,
    preencher_campo,
)
from utils.versao_gen import escopo, get_versao


def garantir_enderecamentos(context: ExecutionContext) -> None:
    """
    Ensures enderecamentos exist according to blueprint.
    """

    page = context.browser_manager.page
    blueprint = context.blueprint
    almoxarifados_data = blueprint.get("almoxarifados")
    materiais_data = blueprint.get("materiais")
    endereco_material_data = blueprint.get("enderecos_material")
    unidade_medida_data = blueprint.get("unidade_medida")

    if not almoxarifados_data:
        logger.info("Nenhum almoxarifado definido no arquivo yaml. Ignorando fluxo.")
        return
    
    if not materiais_data:
        logger.info("Nenhum material definido no arquivo yaml. Ignorando fluxo.")
        return
    
    if not endereco_material_data:
        logger.info("Nenhum endereço de material definido no arquivo yaml. Ignorando fluxo.")
        return
    
    if not unidade_medida_data:
        logger.info("Nenhuma unidade de medida definida no arquivo yaml. Ignorando fluxo.")
        return

    if not acessar_enderecamento(page):
        logger.error("Menu 'Endereçamento de Material' não disponível para este cliente.")
        return

    almoxarifados_total = len(almoxarifados_data)
    materiais_total = len(materiais_data)
    endereco_total = len(endereco_material_data)

    logger.info("Foi encontrado um total de {} almoxarifados no arquivo yaml.", almoxarifados_total)
    logger.info("Foi encontrado um total de {} materiais no arquivo yaml.", materiais_total)
    logger.info("Foi encontrado um total de {} endereços de materiais no arquivo yaml.", endereco_total)

    for indice_almoxarifado, almoxarifado in enumerate(almoxarifados_data, start=1):
        for indice_material, material in enumerate(materiais_data, start=1):

            # Se for o primeiro material, ele faz o endereçamento para todos os endereços.
            if indice_material == 1:
                enderecos_para_usar = endereco_material_data

            # Se não for o 1 material ele faz endereçamento de apenas 1 endereço.
            else:
                enderecos_para_usar = endereco_material_data[:1]

            for indice_endereco, endereco in enumerate(enderecos_para_usar, start=1):

                logger.info(
                    "Almoxarifado {}/{}, Material {}/{} e Endereçamento {}/{}",
                    indice_almoxarifado, 
                    almoxarifados_total, 
                    indice_material, 
                    materiais_total,
                    indice_endereco,
                    endereco_total
                )

                sigla_almoxarifado = almoxarifado["sigla"]
                nome_material = material["nome"]
                complemento = material["complemento"]
                nome_completo_material = f"{nome_material} {complemento}"
                nome_parcial_material = f"{nome_material} {complemento.split()[0]}"

                logger.info(
                    "Garantindo endereçamento para o material '{}', almoxarifado '{}' e endereço '{}'",
                    nome_parcial_material, 
                    sigla_almoxarifado,
                    endereco["descricao"]
                )

                if enderecamento_existe(page, sigla_almoxarifado, nome_completo_material, endereco):
                    logger.info(
                        "Endereçamento '{}' para o material '{}' e almoxarifado '{}' já existe. "
                        "Nenhuma ação necessária.", 
                        endereco["descricao"],
                        nome_parcial_material, 
                        sigla_almoxarifado
                    )
                    continue
                
                logger.info(
                    "Endereçamento '{}' para o material '{}' e almoxarifado '{}' "
                    "não encontrado. Criando...", 
                    endereco["descricao"],
                    nome_parcial_material, 
                    sigla_almoxarifado
                )
                
                _criar_enderecamento(
                    page, 
                    almoxarifado, 
                    material, 
                    endereco, 
                    unidade_medida_data
                )

                # --- Post-creation validation ---
                if not enderecamento_existe(page, sigla_almoxarifado, nome_completo_material, endereco):
                    raise RuntimeError(
                        f"Falha ao validar criação de endereço '{endereco['descricao']}' para o material "
                        f"'{nome_parcial_material}' e almoxarifado {sigla_almoxarifado}."
                    )

                logger.success(
                    "Endereçamento para o material '{}' e almoxarifado " 
                    "'{}' criado com sucesso.", 
                    nome_parcial_material, 
                    sigla_almoxarifado
                )


def _criar_enderecamento(
    page: Page, 
    almoxarifado: dict, 
    material: dict, 
    endereco: dict, 
    unidade_medida: dict
) -> None:
    """
    Performs deterministic creation of enderecamento.
    Assumes prior existence check returned False.
    """
    sigla_almoxarifado = almoxarifado["sigla"]
    nome_material = f"{material['nome']} {material['complemento']}"
    codigo_endereco = endereco["codigo"]
    sigla_um = unidade_medida["sigla"]

    if not acessar_enderecamento(page):
        logger.error("Menu 'Endereçamento de Material' não disponível para este cliente.")
        return

    ctx = escopo(page)
    is_v3 = get_versao() == 3
    is_ja_selecionado = material_ja_selecionado(ctx, nome_material)

    if not is_ja_selecionado:
        if is_v3:
            campo_almoxarifado = ctx.locator("input[name='almoxarifado']")
            if campo_almoxarifado.is_disabled():
                ctx.locator("button[name='submitNew']").click()
                aguardar_ajax_global(page)
        else:
            ctx.locator("button[name='submitNew']").click()
            aguardar_ajax_global(page)

        preencher_campo(ctx, "input[name='almoxarifado']", sigla_almoxarifado)
        preencher_campo(ctx, "input[name='material']", nome_material)
        aguardar_ajax_global(page)

    ctx.locator("button[name='submitAddLine1']").click()
    aguardar_ajax_global(page)

    linhas = ctx.locator("table.tabela tbody tr")

    for i in range(linhas.count()):
        linha = linhas.nth(i)
        campo_endereco = linha.locator("td").nth(2).locator("input[type='text']")
        campo_sigla_um = linha.locator("td").nth(3).locator("input[type='text']")

        if is_v3:
            is_empty = campo_endereco.is_editable() and campo_sigla_um.is_editable()
        else:
            is_empty = campo_endereco.input_value() == "" and campo_sigla_um.input_value() == ""

        if is_empty:
            preencher_campo(ctx, campo_endereco, codigo_endereco)
            preencher_campo(ctx, campo_sigla_um, sigla_um)
            break

    aguardar_ajax_global(page)

    ctx.get_by_role("button", name="Confirmar").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    ctx.get_by_role("button", name="Novo").click()
    aguardar_ajax_global(page)
