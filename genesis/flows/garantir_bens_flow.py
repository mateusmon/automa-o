from random import randint

from loguru import logger
from playwright.sync_api import Page, expect

from engine.execution_context import ExecutionContext
from navigation.navegar_para_bem import acessar_bem
from services.bem_service import bem_existe
from utils.espera import (
    aguardar_ajax_global,
    esperar_sucesso_ou_erro,
    preencher_campo,
)
from utils.versao_gen import escopo, get_versao


def garantir_bens(context: ExecutionContext) -> None:
    """
    Ensures bens exist according to blueprint.
    """
    page = context.browser_manager.page
    blueprint = context.blueprint
    bens_data = blueprint.get("bens")

    if not bens_data:
        logger.info("Nenhum bem definido no arquivo yaml. Ignorando fluxo.")
        return

    total = len(bens_data)
    logger.info("Foi encontrado um total de {} bens no arquivo yaml.", total)

    for atual, bem in enumerate(bens_data, start=1):
        logger.info("Bem {}/{}", atual, total)

        nome_bem = bem["nome"]
        complemento_bem = bem["complemento"]
        nome_completo = f"{nome_bem} {complemento_bem}"

        logger.info("Garantindo bem nome '{}'", nome_completo)

        if bem_existe(page, nome_bem):
            logger.info("Bem '{}' já existe. Nenhuma ação necessária.", nome_completo)
            continue

        logger.info("Bem '{}' não encontrado. Criando...", nome_completo)
        _criar_bem(page, bem)

        # --- Post-creation validation ---
        if not bem_existe(page, nome_bem):
            raise RuntimeError(
                f"Falha ao validar criação de bem '{nome_completo}'."
            )

        logger.success("Bem '{}' criado com sucesso.", nome_completo)


def _criar_bem(page: Page, bem_data: dict) -> None:
    """
    Performs deterministic creation of bem.
    Assumes prior existence check returned False.
    """
    nome_bem = bem_data["nome"]
    complemento_bem = bem_data["complemento"]

    acessar_bem(page)

    ctx = escopo(page)

    if ctx.locator("textarea[name='complemento_NmBemServico']").input_value() != "":
        ctx.get_by_role("button", name="Novo").click()
        aguardar_ajax_global(page)

    _selecionar_subgrupo(page, ctx, bem_data)

    ctx.locator("button[name='submitAddLine1']").click()
    aguardar_ajax_global(page)

    # Filling name of bem
    ctx.locator("input[name='material_DsBemGenerico']").fill(nome_bem)

    # Filling complement of bem
    ctx.locator("textarea[name='complemento_NmBemServico']").fill(complemento_bem)
    aguardar_ajax_global(page)

    # Clicking out of the input field so that the page refreshes
    if get_versao() >= 4:
        page.get_by_role("heading", name="Material - Permanente").click()
    else:
        ctx.get_by_role("heading", name="Material", exact=True).click()
    aguardar_ajax_global(page)

    # Preenchendo unidade de medida com a primeira que estiver disponível
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


def _selecionar_subgrupo(page: Page, ctx, bem_data: dict[str, str]) -> None:
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


def _selecionar_conta_aleatoria(page: Page, ctx) -> None:
    ctx.locator("button[name='lookup-complemento_CdConta']").click()
    aguardar_ajax_global(page)

    linhas = ctx.locator("table[name='paginationTable'] tbody tr").filter(
        has_not_text="ESTOQUE"
    )
    linhas.nth(0).wait_for(state="visible")

    total_linhas = linhas.count()
    if total_linhas == 0:
        raise ValueError("Nenhuma conta contábil sem estoque disponível.")

    linha_aleatoria = randint(0, total_linhas - 1)

    # Choosing a random accounting account
    linhas.nth(linha_aleatoria).locator("button[name='submitUse']").click()
    aguardar_ajax_global(page)
