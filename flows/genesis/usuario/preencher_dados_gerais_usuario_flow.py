"""Dados gerais do cadastro persistente de Usuário Genesis."""

from loguru import logger
from playwright.sync_api import Frame, Page

from flows.genesis.shared.preencher_lookup_flow import preencher_campo
from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def preencher_dados_gerais_usuario(page: Page, usuario: dict) -> None:
    """Abre o cadastro e preenche Funcionário e Senha, sem confirmar. Cenário A."""
    logger.info("Iniciou preenchimento de dados gerais de Usuário '{}'.", usuario["nome"])
    ctx = escopo(page)
    _abrir_formulario(page, ctx)
    preencher_campo(ctx, "input[name='funcionario']", usuario["nome"])
    ctx.locator("input[name='senha']").fill(usuario["senha"])
    ctx.locator("input[name='confirmacaoSenha']").fill(usuario["senha"])
    logger.info("Finalizou preenchimento de dados gerais de Usuário '{}'.", usuario["nome"])


def _abrir_formulario(page: Page, ctx: Page | Frame) -> None:
    """
    Garante que o formulário de cadastro esteja aberto e editável.

    """
    campo = ctx.locator("input[name='funcionario']")

    try:
        campo.wait_for(state="visible", timeout=5_000)
        if not campo.is_disabled():
            return
    except Exception:
        logger.debug("Formulário de usuário não está aberto. Clicando em 'Novo'.")

    ctx.get_by_role("button", name="Novo").click()
    aguardar_ajax_global(page)

    campo.wait_for(state="visible", timeout=30_000)


