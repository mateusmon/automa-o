from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, proximo_nome


def alterar_modelo_importacao(page: Page) -> None:
    """
    Altera a Descrição do Modelo de Importação (`dsModelo`) e confirma UMA vez (sem desfazer).

    Convenção vigente: uma única confirmação (ao salvar, a tela pode recarregar e limpar os
    dados, o que quebraria um segundo submit) e alteração do Nome sempre por ADIÇÃO de sufixo
    (" ALT"/" TLA"), mantendo o registro localizável pela Consulta e o teste re-executável.
    Não mexe em checkbox/radio. Cenário A. Pressupõe o modelo já carregado (ver `selecionar_modelo_importacao`).
    """
    logger.info("Iniciou alteração de Modelo de Importação.")

    ctx = escopo(page)
    campo = ctx.locator("input[name='dsModelo']")
    campo.fill(proximo_nome(campo.input_value()))

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou alteração de Modelo de Importação.")
