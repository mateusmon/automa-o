from loguru import logger
from playwright.sync_api import Page

from engine.execution_context import ExecutionContext
from navigation.navegar_para_ul import acessar_ul
from services.ul_service import ul_existe
from utils.espera import (
    aguardar_ajax_global,
    esperar_sucesso_ou_erro,
    preencher_campo,
)
from utils.versao_gen import escopo


def garantir_uls(context: ExecutionContext) -> None:
    """
    Ensures uls exist according to blueprint.
    """
    page = context.browser_manager.page
    blueprint = context.blueprint
    uls_data = blueprint.get("unidades_localizacao")

    if not uls_data:
        logger.info("Nenhuma UL definida no arquivo yaml. Ignorando fluxo.")
        return

    total = len(uls_data)
    logger.info("Foi encontrado um total de {} unidades de localização no arquivo yaml.", total)

    for atual, ul in enumerate(uls_data, start=1):
        logger.info("Unidade de localização {}/{}", atual, total)

        endereco_ul = ul["endereco"]
        sigla_ul = ul["sigla"]

        logger.info("Garantindo unidade de localização endereço '{}'", endereco_ul)

        if ul_existe(page, endereco_ul):
            logger.info("Unidade de localização '{}' já existe. Nenhuma ação necessária.", sigla_ul)
            continue

        logger.info("Unidade de localização '{}' não encontrada. Criando...", sigla_ul)
        _criar_ul(page, ul)

        # --- Post-creation validation ---
        if not ul_existe(page, endereco_ul):
            raise RuntimeError(f"Falha ao validar criação de unidade de localização '{sigla_ul}'.")

        logger.success("Unidade de localização '{}' criada com sucesso.", sigla_ul)


def _criar_ul(page: Page, ul_data: dict) -> None:
    """
    Performs deterministic creation of ul.
    Assumes prior existence check returned False.
    """
    acessar_ul(page)

    ctx = escopo(page)

    if ctx.locator("input[name='sgUl']").input_value() != "":
        ctx.locator("button[name='submitNew']").click()
        aguardar_ajax_global(page)

    _preencher_dados(page, ctx, ul_data)


def _preencher_dados(page: Page, ctx, ul_data: dict) -> None:
    sigla_ul = ul_data["sigla"]
    endereco_ul = ul_data["endereco"]
    ua_ul = ul_data["unidade_administrativa"]
    responsavel_ul = ul_data.get("responsavel", {})
    nome_responsavel_ul = responsavel_ul["nome"]
    funcao_responsavel_ul = responsavel_ul["funcao"]

    field_sigla = ctx.locator("input[name='sgUl']")
    field_sigla.click()
    field_sigla.fill(sigla_ul)

    preencher_campo(ctx, "input[name='ua']", ua_ul)
    try:
        preencher_campo(ctx, "input[name='centroCusto']", ul_data["centro_custo"])
    except Exception:
        ctx.locator("button[name='submitCancel']").click()
        aguardar_ajax_global(page)
        logger.warning(
            "Não foi possível preencher centro de custos {}. "
            "Preenchendo com o primeiro disponível", 
            ul_data["centro_custo"]
        )
        preencher_campo(ctx, "input[name='centroCusto']", "   ")

    field_endereco = ctx.locator("input[name='local']")
    field_endereco.click()
    field_endereco.fill(endereco_ul)
    ctx.locator("button[name='lookup-local']").click()
    aguardar_ajax_global(page)

    ctx.locator("button[name='submitTabResponsaveis']").click()
    aguardar_ajax_global(page)

    tbody = ctx.locator("table.tabela tbody")
    tbody.wait_for(state="visible")

    preencher_campo(ctx, "input[name='hierarquia-1-2']", nome_responsavel_ul)
    preencher_campo(ctx, "input[name='tipoFuncao-1-3']", funcao_responsavel_ul)

    ctx.locator("input[name='hierarquia-1-5']").click()
    ctx.locator("button[name='submitFinish']").click()

    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)
