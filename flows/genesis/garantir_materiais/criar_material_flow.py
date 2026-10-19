import random
from typing import Any

from loguru import logger
from playwright.sync_api import Page, expect

from utils.versao import escopo, get_versao
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo


def criar_material(page: Page, materiais_faltantes: list[dict[str, Any]]) -> None:
    """Realiza o cadastro determinístico de todos os materiais pendentes."""
    if not materiais_faltantes:
        return

    logger.info(f"Iniciando criação de {len(materiais_faltantes)} material(is)...")

    for material in materiais_faltantes:
        logger.info("Criando material '{}'...", material["nome"])
        _preencher_formulario_material(page, material)

    logger.info("Criação de materiais concluída.")


def _preencher_formulario_material(page: Page, material_data: dict[str, Any]) -> None:
    """Preenche os campos da interface para um único material de consumo."""
    nome_material = material_data["nome"]
    complemento_material = material_data["complemento"]

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

    # Preenche complemento
    ctx.locator("textarea[name='complemento_NmBemServico']").fill(complemento_material)
    aguardar_ajax_global(page)

    # Dispara validação/ajax
    if get_versao() >= 4:
        page.get_by_role("heading", name="Material - Consumo").click()
    else:
        ctx.get_by_role("heading", name="Material", exact=True).click()
    aguardar_ajax_global(page)

    _selecionar_conta(page, ctx)
    aguardar_ajax_global(page)

    # Preenche Unidade de Medida
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


def _selecionar_subgrupo(page: Page, ctx: Any, bem_data: dict[str, Any]) -> None:
    ctx.locator("button[name='submitFinish']").wait_for(state="visible")

    preencher_campo(ctx, "input[name='subgrupo']", bem_data["subgrupo"])

    aviso = ctx.locator("text=Nenhum SUBGRUPO encontrado!")
    subgrupo = ctx.locator("img[title='Retornar']").first
    expect(aviso.or_(subgrupo)).to_be_visible()

    if aviso.is_visible():
        ctx.locator(".x-btn-center button:has-text('OK')").click()
        aguardar_ajax_global(page)
        _selecionar_subgrupo_federal_supply(page, ctx, bem_data)
        return

    subgrupo.click()
    aguardar_ajax_global(page)


def _selecionar_subgrupo_federal_supply(
    page: Page, ctx: Any, bem_data: dict[str, Any]
) -> None:
    ctx.locator("button[name='federalSupply']").click()
    aguardar_ajax_global(page)

    ctx.locator("input[name='filtro']").fill(bem_data["subgrupo"])
    ctx.locator("button[name='lookup-filtro']").click()
    aguardar_ajax_global(page)

    ctx.locator("img.x-tree-node-icon.icon-subgrupo-open").dblclick()
    aguardar_ajax_global(page)


def _selecionar_conta(page: Page, ctx: Any) -> None:
    ctx.locator("button[name='lookup-complemento_CdConta']").click()
    aguardar_ajax_global(page)

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


def _ativar_material_cadastrado(page: Page, ctx: Any, complemento: str) -> None:
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
