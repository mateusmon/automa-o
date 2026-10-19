from loguru import logger
from playwright.sync_api import Page

from engine.execution_context import ExecutionContext
from navigation.navegar_para_instalacao import acessar_instalacao
from services.instalacao_service import instalacao_existe
from utils.espera import (
    aguardar_ajax_global,
    escolher_cidade,
    esperar_sucesso_ou_erro,
)
from utils.versao_gen import escopo


def garantir_instalacao(context: ExecutionContext) -> None:
    """
    Ensures instalacao exists according to blueprint.
    """

    page = context.browser_manager.page
    blueprint = context.blueprint
    instalacao_data = blueprint.get("instalacao")

    if not instalacao_data:
        logger.info("Nenhuma instalação definida no arquivo yaml. Ignorando fluxo.")
        return

    if not acessar_instalacao(page):
        logger.warning("Menu 'Instalação' não disponível para este cliente. Pulando fluxo de instalação.")
        return

    nome = instalacao_data["nome"]

    logger.info("Garantindo instalação com nome '{}'", nome)

    if instalacao_existe(page, nome):
        logger.info("Instalação '{}' já existe. Nenhuma ação necesária.", nome)
        return

    logger.info("Instalação '{}' não encontrada. Criando...", nome)

    _criar_instalacao(page, instalacao_data)

    if not instalacao_existe(page, nome):
        raise RuntimeError(
            f"Falha ao validar criação da instalação '{nome}'."
        )

    logger.success("Instalação '{}' criada com sucesso.", nome)


def _criar_instalacao(page: Page, instalacao_data: dict) -> None:
    """
    Performs deterministic creation of instalacao.
    Assumes prior existence check returned False.
    """
    nome = instalacao_data["nome"]
    endereco = instalacao_data["endereco"]
    cidade = instalacao_data["cidade"]

    if not acessar_instalacao(page):
        logger.warning("Menu 'Instalação' não disponível para este cliente. Impossível criar instalação.")
        return

    ctx = escopo(page)

    escolher_cidade(ctx, cidade, locator_campo="input[name='cidade']")

    ctx.locator("input[name='nmInstalacao']").fill(nome)
    ctx.locator("input[name='dsEndereco']").fill(endereco)

    _aceitar_dialog_se_aparecer(page)

    ctx.get_by_role("button", name="Confirmar").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)


def _aceitar_dialog_se_aparecer(page: Page) -> None:
    def handle_dialog(dialog):
        logger.warning("Diálogo detectado e aceito: {}", dialog.message)
        dialog.accept()

    page.once("dialog", handle_dialog)