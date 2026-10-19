from engine.execution_context import ExecutionContext
from loguru import logger
from navigation.navegar_para_funcionario import acessar_funcionario
from playwright.sync_api import Page
from services.funcionario_service import funcionario_existe
from utils.dados_locais import funcionarios_para_garantir
from utils.espera import (
    aguardar_ajax_global,
    esperar_sucesso_ou_erro,
    obter_frame_conteudo,
    preencher_campo,
)
from utils.versao_gen import get_versao


def garantir_funcionarios(context: ExecutionContext) -> None:
    """
    Ensures funcionarios exists according to blueprint.
    """

    page = context.browser_manager.page
    funcionarios_data = funcionarios_para_garantir(context)

    if not funcionarios_data:
        logger.info("Nenhum funcionário definido no arquivo yaml ou local. Ignorando fluxo.")
        return

    if not acessar_funcionario(page):
        logger.warning(
            "Menu 'Funcionário' não disponível para este cliente. Pulando fluxo de funcionários."
        )
        return

    total = len(funcionarios_data)

    logger.info("Foi encontrado um total de {} funcionários nos arquivos yaml e local.", total)

    for atual, funcionario in enumerate(funcionarios_data, start=1):
        logger.info("Funcionário {}/{}", atual, total)

        matricula = funcionario["matricula"]

        logger.info("Garantindo funcionário matrícula '{}'", matricula)

        if funcionario_existe(page, matricula):
            logger.info("Funcionário '{}' já existe. Nenhuma ação necesária.", matricula)
            continue

        logger.info("Funcionário '{}' não encontrado. Criando...", matricula)

        _criar_funcionario(page, funcionario)

        if not funcionario_existe(page, matricula):
            raise RuntimeError(f"Falha ao validar criação do funcionário '{matricula}'.")

        logger.success("Funcionário '{}' criado com sucesso.", matricula)


def _criar_funcionario(page: Page, funcionario: dict) -> None:
    """
    Performs deterministic creation of funcionario.
    Assumes prior existence check returned False.
    """
    nome = funcionario["nome"]
    email = funcionario["email"]
    matricula = funcionario["matricula"]
    cpf = f"{matricula[:3]}.{matricula[3:6]}.{matricula[6:9]}-{matricula[9:]}"

    if not acessar_funcionario(page):
        logger.warning(
            "Menu 'Funcionário' não disponível para este cliente. Impossível criar funcionário."
        )
        return

    if get_versao() >= 4:
        ctx = obter_frame_conteudo(page)
        assert ctx is not None
    else:
        ctx = page

    matricula_is_disabled = ctx.locator("input[name='cdFuncionario']").is_disabled(timeout=1_000)
    if matricula_is_disabled:
        ctx.get_by_role("button", name="Novo").click()
        aguardar_ajax_global(page)

    ctx.locator("input[name='cdFuncionario']").fill(matricula)

    label_ua = ctx.locator("label[for=cdUa]")
    texto = label_ua.inner_text().strip()
    tem_asterisco = "*" in texto

    # If UA is obligatory, fill it with the first UA available
    if tem_asterisco:
        lookup = ctx.locator(
            "button[name='lookup-cdUa'], "
            "button[name='lookup-ccdUa']"  # nome errado encontrado na SEADPB
        ).first

        lookup_name = lookup.get_attribute("name")

        preencher_campo(
            ctx,
            "input[name='cdUa']",
            "   ",
            lookup_name=lookup_name,
        )

    ctx.locator("input[name='nmRegistroCivil']").fill(nome)
    ctx.locator("input[name='nrCpf']").fill(cpf)
    ctx.locator("input[name='nmEmail']").fill(email)

    ctx.get_by_role("button", name="Confirmar").click()

    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)
