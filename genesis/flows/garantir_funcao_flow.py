from loguru import logger
from playwright.sync_api import Page

from engine.execution_context import ExecutionContext
from navigation.navegar_para_funcao import acessar_funcao
from services.funcao_service import funcao_existe
from utils.espera import (
    aguardar_ajax_global,
    esperar_sucesso_ou_erro,
    obter_frame_conteudo,
)
from utils.versao_gen import get_versao


def garantir_funcao(context: ExecutionContext) -> None:
    """
    Ensures funcao exists according to blueprint.
    """

    page = context.browser_manager.page
    blueprint = context.blueprint
    funcao_data = blueprint.get("funcao")

    if not funcao_data:
        logger.info("Nenhuma função definida no arquivo yaml. Ignorando fluxo.")
        return

    if not acessar_funcao(page):
        logger.warning("Menu 'Funções' não disponível para este cliente. Pulando fluxo de função.")
        return

    nome_funcao = funcao_data["nome"]

    logger.info("Garantindo função nome '{}'", nome_funcao)

    if funcao_existe(page, nome_funcao):
        logger.info("Função '{}' já existe. Nenhuma ação necesária.", nome_funcao)
        return

    logger.info("Função '{}' não encontrada. Criando...", nome_funcao)

    _criar_funcao(page, funcao_data)

    if not funcao_existe(page, nome_funcao):
        raise RuntimeError(
            f"Falha ao validar criação de função '{nome_funcao}'."
        )

    logger.success("Função '{}' criada com sucesso.", nome_funcao)


def _criar_funcao(page: Page, funcao_data: dict) -> None:
    """
    Performs deterministic creation of funcao.
    Assumes prior existence check returned False.
    """
    nome_funcao = funcao_data["nome"]

    if not acessar_funcao(page):
        logger.warning("Menu 'Funções' não disponível para este cliente. Impossível criar função.")
        return

    if get_versao() >= 4:
        ctx = obter_frame_conteudo(page)
        assert ctx is not None
    else:
        ctx = page

    ctx.locator("input[name='nmTpFuncaoHier']").fill(nome_funcao)

    ctx.get_by_role("button", name="Confirmar").click()

    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)