from engine.execution_context import ExecutionContext
from loguru import logger
from playwright.sync_api import Page
from navigation.navegar_para_orgao_externo import acessar_orgao_externo
from services.orgao_externo_service import orgao_externo_existe
from utils.espera import (
    aguardar_ajax_global,
    escolher_cidade,
    esperar_sucesso_ou_erro,
)
from utils.versao_gen import escopo


def garantir_orgao_externo(context: ExecutionContext) -> None:
    page = context.browser_manager.page
    blueprint = context.blueprint
    orgao_externo_data = blueprint.get("orgao_externo")

    if not orgao_externo_data:
        logger.info("Nenhum órgão externo definido no arquivo yaml. Ignorando fluxo.")
        return

    if not acessar_orgao_externo(page):
        logger.error("Menu 'Órgão Externo' não disponível para este cliente.")
        return

    nome = orgao_externo_data["nome"]

    logger.info("Garantindo órgão externo '{}'", nome)

    if orgao_externo_existe(page, nome):
        logger.info("Órgão externo '{}' já existe. Nenhuma ação necessária.", nome)
        return

    logger.info("Órgão externo '{}' não encontrado. Criando...", nome)

    _criando_orgao_externo(page, orgao_externo_data)

    # --- Post-creation validation ---
    if not orgao_externo_existe(page, nome):
        raise RuntimeError(
            f"Falha ao validar criação do órgão externo '{nome}'."
        )

    logger.success("Órgão externo '{}' criado com sucesso.", nome)


def _criando_orgao_externo(page: Page, orgao_externo_data: dict[str, str]) -> None:
    if not acessar_orgao_externo(page):
        logger.error("Menu 'Órgão Externo' não disponível para este cliente.")
        return

    ctx = escopo(page)
    aguardar_ajax_global(page)
    ctx.locator("input[name='nrIdentAgente']").wait_for(state="visible")

    ctx.locator("input[name='nrIdentAgente']").fill(_formatar_cnpj(orgao_externo_data["cnpj"]))
    ctx.locator("input[name='nmAgente']").fill(orgao_externo_data["nome"])
    ctx.locator("input[name='sgOrgaoExterno']").fill(orgao_externo_data["sigla"])
    ctx.locator("input[name='edAgente']").fill(orgao_externo_data["endereco"])
    ctx.locator("input[name='nmBairro']").fill(orgao_externo_data["bairro"])

    escolher_cidade(ctx, orgao_externo_data["cidade"])

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)


def _formatar_cnpj(cnpj: str) -> str:
    """Formata 14 dígitos como XX.XXX.XXX/XXXX-XX."""
    if not cnpj.isdigit() or len(cnpj) != 14:
        raise ValueError(f"CNPJ inválido para formatação: {cnpj}")
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
