from random import randint
from typing import Any

from loguru import logger
from playwright.sync_api import Page, expect

from flows.corporativo.material.cadastro_material_permanente.navegar_para_material_permanente_flow import (
    acessar_material_permanente,
)
from utils.versao import escopo, get_versao
from utils.waits import (
    aguardar_ajax_global,
    esperar_sucesso_ou_erro,
    preencher_campo,
)


def criar_bem(page: Page, bens_faltantes: list[dict[str, Any]]) -> None:
    """Fluxo para cadastro sequencial dos bens faltantes."""
    if not bens_faltantes:
        return

    total = len(bens_faltantes)

    for atual, bem in enumerate(bens_faltantes, start=1):
        nome_completo = f"{bem['nome']} {bem['complemento']}"

        logger.info("Bem {}/{}", atual, total)
        logger.info("Garantindo bem nome '{}'", nome_completo)
        logger.info("Bem '{}' não encontrado. Criando...", nome_completo)

        _preencher_formulario_bem(page, bem)

        logger.info("Bem '{}' criado com sucesso.", nome_completo)


def _preencher_formulario_bem(page: Page, bem_data: dict[str, Any]) -> None:
    nome_bem = bem_data["nome"]
    complemento_bem = bem_data["complemento"]

    acessar_material_permanente(page)

    ctx = escopo(page)

    if ctx.locator("textarea[name='complemento_NmBemServico']").input_value() != "":
        ctx.get_by_role("button", name="Novo").click()
        aguardar_ajax_global(page)

    _selecionar_subgrupo(page, ctx, bem_data)

    ctx.locator("button[name='submitAddLine1']").click()
    aguardar_ajax_global(page)

    ctx.locator("input[name='material_DsBemGenerico']").fill(nome_bem)
    ctx.locator("textarea[name='complemento_NmBemServico']").fill(complemento_bem)
    aguardar_ajax_global(page)

    if get_versao() >= 4:
        page.get_by_role("heading", name="Material - Permanente").click()
    else:
        ctx.get_by_role("heading", name="Material", exact=True).click()
    aguardar_ajax_global(page)

    tentativas = 0
    while True:
        preencher_campo(ctx, "input[name='complemento_CdUmElementar']", "UN ")
        aguardar_ajax_global(page)

        if ctx.locator("input[name='complemento_CdUmElementar']").input_value().strip():
            break

        tentativas += 1
        if tentativas >= 3:
            raise RuntimeError(
                "Campo de unidade de medida não permaneceu preenchido após 3 tentativas."
            )
        logger.warning("Campo U.M. limpo pelo reload. Repetindo preenchimento.")

    _selecionar_conta_aleatoria(page, ctx)

    status_select = ctx.locator("select[name='tdStatus']")
    if status_select.is_disabled():
        raise RuntimeError("Status do bem desabilitado. Habilite-o no perfil.")

    status_select.select_option(value="01")
    ctx.get_by_role("button", name="Confirmar").click(timeout=90_000)

    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)


def _selecionar_subgrupo(page: Page, ctx: Any, bem_data: dict[str, Any]) -> None:
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


def _selecionar_conta_aleatoria(page: Page, ctx: Any) -> None:
    ctx.locator("button[name='lookup-complemento_CdConta']").click()
    aguardar_ajax_global(page)

    linhas = ctx.locator("table[name='paginationTable'] tbody tr").filter(
        has_not_text="ESTOQUE"
    )

    total_linhas = linhas.count()
    if total_linhas == 0:
        raise ValueError("Nenhuma conta contábil sem estoque disponível.")

    linhas.nth(0).wait_for(state="visible")
    linha_aleatoria = randint(0, total_linhas - 1)

    linhas.nth(linha_aleatoria).locator("button[name='submitUse']").click()
    aguardar_ajax_global(page)
