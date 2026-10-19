from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, proximo_nome


def alterar_almoxarifado(page: Page) -> None:
    """
    Altera a Descrição do Almoxarifado (`dsAlmoxarifado`) e confirma UMA vez (sem desfazer).

    Convenção vigente: uma única confirmação (ao salvar, a tela pode recarregar e limpar os
    dados, o que quebraria um segundo submit) e alteração do Nome sempre por ADIÇÃO de sufixo
    (" ALT"/" TLA"), mantendo o registro localizável pela Consulta e o teste re-executável.
    Não mexe em checkbox/radio. Cenário A. Pressupõe o registro já carregado (ver `selecionar_almoxarifado`).
    """
    ctx = escopo(page)
    campo = ctx.locator("input[name='dsAlmoxarifado']")
    logger.info("Iniciou alteração de Almoxarifado '{}'.", campo.input_value())

    logger.info(
        "Alterando a Descrição do Almoxarifado: '{}' -> '{}'.",
        campo.input_value(),
        proximo_nome(campo.input_value()),
    )
    campo.fill(proximo_nome(campo.input_value()))

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou alteração de Almoxarifado '{}'.", campo.input_value())
