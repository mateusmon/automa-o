from engine.execution_context import ExecutionContext
from loguru import logger
from navigation.navegar_para_funcionario import acessar_funcionario
from playwright.sync_api import Page
from services.associacao_funcionario_ua_service import associacao_existe
from utils.dados_locais import funcionarios_para_garantir
from utils.espera import (
    aguardar_ajax_global,
    esperar_sucesso_ou_erro,
    obter_frame_conteudo,
    preencher_campo,
)
from utils.versao_gen import get_versao


def garantir_associacao_funcionarios_ua(context: ExecutionContext) -> None:
    """
    Ensures there's an association between funcionario and
    unidade administrativa according to blueprint.
    """

    page = context.browser_manager.page
    blueprint = context.blueprint
    funcionarios_data = funcionarios_para_garantir(context)
    ua_data = blueprint.get("unidade_administrativa")

    if not funcionarios_data:
        logger.info("Nenhum funcionário definido no arquivo yaml. Ignorando fluxo.")
        return

    if not ua_data:
        logger.info("Nenhuma unidade administrativa definida no arquivo yaml. Ignorando fluxo.")
        return

    if not acessar_funcionario(page):
        logger.warning(
            "Menu 'Funcionário' não disponível para este cliente. Pulando fluxo de associação funcionário/UA."
        )
        return

    total = len(funcionarios_data)

    logger.info("Foi encontrado um total de {} funcionários no arquivo yaml.", total)

    for atual, funcionario in enumerate(funcionarios_data, start=1):
        logger.info("Funcionário {}/{}", atual, total)

        matricula = funcionario["matricula"]
        sigla_ua = ua_data["sigla"]

        logger.info(
            "Garantindo associação entre funcionário matrícula '{}' e unidade administrativa sigla '{}'",
            matricula,
            sigla_ua,
        )

        if associacao_existe(page, matricula):
            logger.info(
                "Associação entre funcionário '{}' e UA '{}' já existe. Nenhuma ação necesária.",
                matricula,
                sigla_ua,
            )
            continue

        logger.info(
            "Associação entre funcionário '{}' e unidade administrativa '{}' não encontrada. Criando...",
            matricula,
            sigla_ua,
        )

        _criar_associacao_funcionario_ua(page, funcionario, ua_data)

        if not associacao_existe(page, matricula):
            raise RuntimeError(
                f"Falha ao validar associação de funcionário '{matricula}' e unidade administrativa '{sigla_ua}'."
            )

        logger.success(
            "Associação entre funcionário '{}' e unidade administrativa '{}' feita com sucesso.",
            matricula,
            sigla_ua,
        )


def _criar_associacao_funcionario_ua(page: Page, funcionario_data: dict, ua_data: dict) -> None:
    """
    Performs deterministic association of funcionario and unidade administrativa.
    Assumes prior existence check returned False.
    """
    sigla_ua = ua_data["sigla"]
    matricula = funcionario_data["matricula"]

    if not acessar_funcionario(page):
        logger.warning(
            "Menu 'Funcionário' não disponível para este cliente. Impossível criar associação."
        )
        return

    if get_versao() >= 4:
        ctx = obter_frame_conteudo(page)
        assert ctx is not None
    else:
        ctx = page

    # Open consultation
    ctx.get_by_role("button", name="Consulta", exact=True).click()
    aguardar_ajax_global(page)

    # Search
    campo_cpf = ctx.locator("#model-4")
    campo_cpf.clear()
    campo_cpf.fill(_format_cpf(matricula))

    ctx.get_by_title("Consultar novo registro").click()
    aguardar_ajax_global(page)

    ctx.wait_for_selector("table[name='paginationTable']")
    ctx.locator("button[name='submitUse']").click()
    aguardar_ajax_global(page)

    preencher_campo(ctx, "input[name='cdUa']", sigla_ua, lookup_name="lookup-ccdUa")

    ctx.get_by_role("button", name="Confirmar").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)


def _format_cpf(cpf: str) -> str:
    if not cpf.isdigit() or len(cpf) != 11:
        raise ValueError(f"CPF inválido para formatação: {cpf}")

    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
