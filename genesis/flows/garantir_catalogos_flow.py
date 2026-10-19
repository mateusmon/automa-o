from loguru import logger
from playwright.sync_api import Page, expect

from engine.execution_context import ExecutionContext
from navigation.navegar_para_catalogo import acessar_catalogo
from services.catalogo_service import catalogo_existe
from utils.espera import (
    aguardar_ajax_global,
    esperar_sucesso_ou_erro,
    preencher_campo,
)
from utils.versao_gen import escopo, get_versao


def garantir_catalogos(context: ExecutionContext) -> None:
    """
    Ensures catalogos exist according to blueprint.
    """
    page = context.browser_manager.page
    blueprint = context.blueprint
    catalogo_data = blueprint.get("catalogo")
    almoxarifados_data = blueprint.get("almoxarifados")
    urs_data = blueprint.get("unidades_requisicao")

    if not catalogo_data:
        logger.info("Nenhum catálogo definido no arquivo yaml. Ignorando fluxo.")
        return

    if not almoxarifados_data:
        logger.info("Nenhum almoxarifado definido no arquivo yaml. Ignorando fluxo.")
        return

    if not urs_data:
        logger.info("Nenhuma UR encontrada no arquivo yaml. Ignorando fluxo.")
        return

    total = len(almoxarifados_data)
    nome_catalogo = catalogo_data["nome"]

    logger.info("Foi encontrado um total de {} almoxarifados no arquivo yaml.", total)

    for atual, almoxarifado in enumerate(almoxarifados_data, start=1):
        logger.info("Almoxarifado {}/{}", atual, total)

        sigla_almoxarifado = almoxarifado["sigla"]
        logger.info("Garantindo catálogo para almoxarifado '{}'", sigla_almoxarifado)

        if catalogo_existe(page, sigla_almoxarifado, nome_catalogo):
            logger.info("Catálogo já existe para almoxarifado '{}'.", sigla_almoxarifado)
            continue

        logger.info("Catálogo não encontrado para almoxarifado '{}'. Criando...", sigla_almoxarifado)
        _criar_catalogo(page, catalogo_data, almoxarifado, urs_data)

        # --- Post-creation validation ---
        if not catalogo_existe(page, sigla_almoxarifado, nome_catalogo):
            raise RuntimeError(
                f"Falha ao validar criação de catálogo para almoxarifado '{sigla_almoxarifado}'."
            )

        logger.success("Catálogo criado com sucesso para almoxarifado '{}'.", sigla_almoxarifado)


def _criar_catalogo(page: Page, catalogo_data: dict, almoxarifado: dict, urs: list[dict[str, str]]) -> None:
    """
    Performs deterministic creation of catalogo.
    Assumes prior existence check returned False.
    """
    nome_catalogo = catalogo_data["nome"]
    sigla_almoxarifado = almoxarifado["sigla"]

    acessar_catalogo(page)

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
            logger.warning("Tentativa {} com valor '{}' falhou: {}", tentativa + 1, valor_atual, e)
            if tentativa == 1:
                raise RuntimeError(f"Falha ao selecionar tipo de catálogo após 2 tentativas: {e}")
            page.wait_for_timeout(1_000)

    _selecionar_materiais(page, ctx, sigla_almoxarifado)
    _associar_urs(page, ctx, urs)

    ctx.get_by_role("button", name="Confirmar").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)


def _selecionar_materiais(page: Page, ctx, sigla_almoxarifado: str) -> None:
    ctx.locator("button[name='lookup-bemServOrgao-1-3']").click()
    aguardar_ajax_global(page)

    ctx.locator("input[name='model-1']").fill(sigla_almoxarifado)
    ctx.locator("button[name='lookup-model-1']").click()
    aguardar_ajax_global(page)

    # Puxando todos os materiais que tenham "AUTOMATIZADO" em seus nomes
    ctx.locator("input[name='model-4']").fill("AUTOMATIZADO")
    ctx.get_by_title("Consultar novo registro").click(no_wait_after=True)
    aguardar_ajax_global(page)

    ctx.get_by_role("button", name="Carregar todos").click()
    aguardar_ajax_global(page)


def _associar_urs(page: Page, ctx, urs: list[dict[str, str]]) -> None:
    ctx.locator("button[name='submitTabUR']").click()
    aguardar_ajax_global(page)

    logger.info("Associando catálogo às URs")

    if get_versao() >= 4:
        linhas = ctx.locator("table.tabela tbody tr")
        linhas.wait_for(state="visible")
        total_linhas = linhas.count()

        for ur in urs:
            nome_ur = ur["nome"]
            # Esperando explicitamente pelo dropdown do autocomplete, porque
            with page.expect_request(
                lambda request: "action=autocompleteList" in request.url,
                timeout=2_000,
            ):
                ctx.fill("input[name='cdUr-1-2']", nome_ur)
            # Essas esperas precisam ser extra longas porque é uma das partes mais lentas de todo o sistema
            aguardar_ajax_global(page, timeout=500_000)

            ctx.locator("button[name='lookup-cdUr-1-2']").click(no_wait_after=True)
            aguardar_ajax_global(page, timeout=500_000)

            total_linhas += 1
            expect(linhas).to_have_count(total_linhas, timeout=30_000)
    else:
        for ur in urs:
            nome_ur = ur["nome"]
            # Esperando explicitamente pelo dropdown do autocomplete, porque
            with page.expect_request(
                lambda request: "action=autocompleteList" in request.url,
                timeout=2_000,
            ):
                ctx.fill("input[name='cdUr-1-2']", nome_ur)
            # Essas esperas precisam ser extra longas porque é uma das partes mais lentas de todo o sistema
            aguardar_ajax_global(page, timeout=500_000)

            ctx.locator("button[name='lookup-cdUr-1-2']").click(no_wait_after=True)
            aguardar_ajax_global(page, timeout=500_000)
