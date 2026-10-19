import random

from engine.execution_context import ExecutionContext
from loguru import logger
from navigation.navegar_para_material import acessar_material
from playwright.sync_api import Page, expect
from services.material_service import material_existe
from utils.espera import (
    aguardar_ajax_global,
    esperar_sucesso_ou_erro,
    preencher_campo,
)
from utils.versao_gen import escopo, get_versao


def garantir_materiais(context: ExecutionContext) -> None:
    """
    Ensures materiais exist according to blueprint.
    """
    page = context.browser_manager.page
    blueprint = context.blueprint
    materiais_data = blueprint.get("materiais")

    if not materiais_data:
        logger.info("Nenhum material definido no arquivo yaml. Ignorando fluxo.")
        return

    if not acessar_material(page):
        logger.error("Menu 'Material - Consumo' não disponível para este cliente.")
        return

    total = len(materiais_data)
    logger.info("Foi encontrado um total de {} materiais no arquivo yaml.", total)

    for atual, material in enumerate(materiais_data, start=1):
        logger.info("Material {}/{}", atual, total)

        nome_material = material["nome"]
        logger.info("Garantindo material nome '{}'", nome_material)

        if material_existe(page, nome_material):
            logger.info("Material '{}' já existe. Nenhuma ação necessária.", nome_material)
            continue

        logger.info("Material '{}' não encontrado. Criando...", nome_material)
        _criar_complemento(page, material)

        # --- Post-creation validation ---
        if not material_existe(page, nome_material):
            raise RuntimeError(
                f"Falha ao validar criação de material '{nome_material}'."
            )

        logger.success("Material '{}' criado com sucesso.", nome_material)


def _criar_complemento(page: Page, material_data: dict) -> None:
    """
    Performs deterministic creation of material.
    Assumes prior existence check returned False.
    """
    nome_material = material_data["nome"]
    complemento_material = material_data["complemento"]

    if not acessar_material(page):
        logger.error("Menu 'Material - Consumo' não disponível para este cliente.")
        return

    ctx = escopo(page)

    if ctx.locator("select[name='tdStatus']").is_disabled():
        msg_erro = (
            "Status do material desabilitado. "
            "Para continuar, habilite a permissão no perfil do usuário: "
            "Corporativo > Segurança > Perfil. "
            "Localize o usuário, selecione o perfil 'Corporativo', "
            "clique no ícone de lápis da permissão 'CP0139 - MATERIAL / SERVIÇO - CONSUMO' "
            "e remova a restrição 'AX1007 - CADASTRO MATERIAL EM ANÁLISE'."
        )
        logger.error("{}", msg_erro)
        raise ValueError(msg_erro)

    if ctx.locator("textarea[name='complemento_NmBemServico']").input_value() != "":
        ctx.get_by_role("button", name="Novo").click()
        aguardar_ajax_global(page)

    _selecionar_subgrupo(page, ctx, material_data)

    # Preenche campo do nome do material
    ctx.locator("button[name='submitAddLine1']").click()
    aguardar_ajax_global(page)

    ctx.locator("input[name='material_DsBemGenerico']").fill(nome_material)

    # Preenche campo do complemento do material
    ctx.locator("textarea[name='complemento_NmBemServico']").fill(complemento_material)
    aguardar_ajax_global(page)

    # Clicando no heading para disparar validação/ajax
    if get_versao() >= 4:
        page.get_by_role("heading", name="Material - Consumo").click()
    else:
        ctx.get_by_role("heading", name="Material", exact=True).click()
    aguardar_ajax_global(page)

    _selecionar_conta(page, ctx)
    aguardar_ajax_global(page)

    # Preenchendo unidade de medida com a primeira que estiver disponível
    tentativas = 0
    while True:
        preencher_campo(ctx, "input[name='complemento_CdUmElementar']", "UMT")
        aguardar_ajax_global(page)

        if ctx.locator("input[name='complemento_CdUmElementar']").input_value().strip():
            break

        tentativas += 1
        if tentativas >= 3:
            raise RuntimeError(
                "Campo de unidade de medida não permaneceu preenchido após 3 tentativas."
            )
        logger.warning("Campo U.M. limpo pelo reload. Repetindo preenchimento.")

    ctx.get_by_role("button", name="Confirmar").click(timeout=90_000)
    aguardar_ajax_global(page)

    info = ctx.locator('div[name="divInfoMsg"]')
    error = ctx.locator('div[name="divErrorMsg"]')
    result = info.or_(error).first
    result.wait_for(state="visible")

    if error.count() > 0 and error.first.is_visible():
        _ativar_material_cadastrado(page, ctx, complemento_material)
        return

    ctx.select_option("select[name='tdStatus']", value="01")
    if ctx.locator("select[name='tdStatus']").is_disabled():
        ctx.get_by_role("button", name="Confirmar").click(timeout=90_000)
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)


def _selecionar_subgrupo(page: Page, ctx, bem_data: dict[str, str]) -> None:
    ctx.locator("button[name='submitFinish']").wait_for(state="visible")

    preencher_campo(ctx, "input[name='subgrupo']", bem_data["subgrupo"])

    aviso = ctx.locator("text=Nenhum SUBGRUPO encontrado!")
    subgrupo = ctx.locator("img[title='Retornar']").first
    expect(aviso.or_(subgrupo)).to_be_visible()

    # Se o aviso estiver visível, escolha o grupo e subgrupo pela tabela federal supply
    if aviso.is_visible():
        ctx.locator(".x-btn-center button:has-text('OK')").click()
        aguardar_ajax_global(page)
        _selecionar_subgrupo_federal_supply(page, ctx, bem_data)
        return

    subgrupo.click()
    aguardar_ajax_global(page)


def _selecionar_subgrupo_federal_supply(page: Page, ctx, bem_data: dict[str, str]) -> None:
    ctx.locator("button[name='federalSupply']").click()
    aguardar_ajax_global(page)

    ctx.locator("input[name='filtro']").fill(bem_data["subgrupo"])
    ctx.locator("button[name='lookup-filtro']").click()
    aguardar_ajax_global(page)

    ctx.locator("img.x-tree-node-icon.icon-subgrupo-open").dblclick()
    aguardar_ajax_global(page)


def _selecionar_conta(page: Page, ctx) -> None:
    ctx.locator("button[name='lookup-complemento_CdConta']").click()
    aguardar_ajax_global(page)

    # Essas contas fazem com que campos a mais apareçam para serem preenchidos, então as evitamos
    linhas = (
        ctx.locator("table[name='paginationTable'] tbody tr")
        .filter(has_not_text="HOSPITALAR")
        .filter(has_not_text="¿")
        .filter(has_not_text="ODONTOLOGICO")
        .filter(has_not_text="LABORATORIAL")
        .filter(has_not_text="ESTOQUE")
    )

    total_linhas = linhas.count()
    if total_linhas == 0:
        raise ValueError("Nenhuma conta disponível.")

    linha = linhas.nth(random.randrange(total_linhas))
    linha.locator("button[name='submitUse']").click()
    aguardar_ajax_global(page)


def _ativar_material_cadastrado(page: Page, ctx, complemento: str) -> None:
    row = ctx.locator(".suppMat tbody tr", has_text=complemento)
    row.scroll_into_view_if_needed()

    radio = row.locator("input[type='radio']")
    radio.check()

    if get_versao() >= 4:
        page.get_by_role("heading", name="Material - Consumo").click()
    else:
        ctx.get_by_role("heading", name="Material", exact=True).click()
    aguardar_ajax_global(page)

    ctx.select_option("select[name='tdStatus']", value="01")
    ctx.get_by_role("button", name="Confirmar").click(timeout=90_000)
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)
