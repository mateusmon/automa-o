from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, escolher_cidade, esperar_sucesso_ou_erro


def preencher_dados_basicos_instalacao(page: Page, instalacao: dict) -> None:
    """
    Preenche a Instalação com os mesmos campos e na mesma ordem da criação legada
    (`_criar_instalacao`): Cidade (lookup) → Nome → Endereço, aceita o diálogo de
    confirmação se aparecer e confirma. Não preenche Bairro nem CEP, como o legado.

    :param instalacao: dict do blueprint (nome, endereco, cidade).
    """
    logger.info("Iniciou preenchimento de dados básicos de Instalação '{}'.", instalacao["nome"])

    ctx = escopo(page)

    escolher_cidade(ctx, instalacao["cidade"], locator_campo="input[name='cidade']")

    ctx.locator("input[name='nmInstalacao']").fill(instalacao["nome"])
    ctx.locator("input[name='dsEndereco']").fill(instalacao["endereco"])

    page.once("dialog", _aceitar_dialog)

    ctx.get_by_role("button", name="Confirmar").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou preenchimento de dados básicos de Instalação '{}'.", instalacao["nome"])


def _aceitar_dialog(dialog) -> None:
    logger.warning("Diálogo detectado e aceito: {}", dialog.message)
    dialog.accept()
