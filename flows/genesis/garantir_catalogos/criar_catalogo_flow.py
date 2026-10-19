from typing import Any

from loguru import logger
from playwright.sync_api import Page, expect

from flows.almoxarifado.auxiliares.catalogo_restrito.navegar_para_catalogo_restrito_flow import (
    acessar_catalogo_restrito,
)
from utils.versao import escopo, get_versao
from utils.waits import (
    aguardar_ajax_global,
    esperar_sucesso_ou_erro,
    preencher_campo,
)


def criar_catalogo(
    page: Page,
    catalogos_faltantes: list[dict[str, Any]],
    catalogo_data: dict[str, Any],
    urs_data: list[dict[str, Any]],
) -> None:
    """Realiza o cadastro sequencial de catálogos para os almoxarifados faltantes."""
    if not catalogos_faltantes:
        return

    logger.info(
        f"Iniciando criação de catálogo para {len(catalogos_faltantes)} almoxarifado(s)..."
    )

    for almoxarifado in catalogos_faltantes:
        _preencher_formulario_catalogo(page, catalogo_data, almoxarifado, urs_data)

    logger.info("Criação de catálogos concluída.")


def _preencher_formulario_catalogo(
    page: Page,
    catalogo_data: dict[str, Any],
    almoxarifado: dict[str, Any],
    urs: list[dict[str, Any]],
) -> None:
    nome_catalogo = catalogo_data["nome"]
    sigla_almoxarifado = almoxarifado["sigla"]

    acessar_catalogo_restrito(page)

    ctx = escopo(page)

    if ctx.locator("input[name='cdAlmoxarifado']").input_value() != "":
        ctx.get_by_role("button", name="Novo").click()
        aguardar_ajax_global(page)

    preencher_campo(ctx, "input[name='cdAlmoxarifado']", sigla_almoxarifado)
    ctx.locator("input[name='dsCatalogo']").fill(nome_catalogo)

    valores = ["REQUISITANTES", "001"]
    for tentativa in range(2):
        try:
            valor_atual = valores[tentativa]
            preencher_campo(ctx, "input[name='cdTipoCatalogo']", valor_atual)
            break
        except Exception as e:
            logger.warning(
                "Tentativa {} com valor '{}' falhou: {}",
                tentativa + 1,
                valor_atual,
                e,
            )
            if tentativa == 1:
                raise RuntimeError(
                    f"Falha ao selecionar tipo de catálogo após 2 tentativas: {e}"
                )
            page.wait_for_timeout(1_000)

    _selecionar_materiais(page, ctx, sigla_almoxarifado)
    _associar_urs(page, ctx, urs)

    ctx.get_by_role("button", name="Confirmar").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)


def _selecionar_materiais(page: Page, ctx: Any, sigla_almoxarifado: str) -> None:
    ctx.locator("button[name='lookup-bemServOrgao-1-3']").click()
    aguardar_ajax_global(page)

    ctx.locator("input[name='model-1']").fill(sigla_almoxarifado)
    ctx.locator("button[name='lookup-model-1']").click()
    aguardar_ajax_global(page)

    # Busca todos os materiais que tenham "AUTOMATIZADO" em seus nomes
    ctx.locator("input[name='model-4']").fill("AUTOMATIZADO")
    ctx.get_by_title("Consultar novo registro").click(no_wait_after=True)
    aguardar_ajax_global(page)

    ctx.get_by_role("button", name="Carregar todos").click()
    aguardar_ajax_global(page)


def _associar_urs(page: Page, ctx: Any, urs: list[dict[str, Any]]) -> None:
    ctx.locator("button[name='submitTabUR']").click()
    aguardar_ajax_global(page)

    logger.info("Associando catálogo às URs")

    is_v4 = get_versao() >= 4
    if is_v4:
        linhas = ctx.locator("table.tabela tbody tr")
        linhas.wait_for(state="visible")
        total_linhas = linhas.count()

    for ur in urs:
        nome_ur = ur["nome"]
        with page.expect_request(
            lambda request: "action=autocompleteList" in request.url,
            timeout=5_000,
        ):
            ctx.fill("input[name='cdUr-1-2']", nome_ur)

        aguardar_ajax_global(page, timeout=500_000)

        ctx.locator("button[name='lookup-cdUr-1-2']").click(no_wait_after=True)
        aguardar_ajax_global(page, timeout=500_000)

        if is_v4:
            total_linhas += 1
            expect(linhas).to_have_count(total_linhas, timeout=30_000)
