from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, proximo_nome


def alterar_definicao_caracteristica(page: Page) -> None:
    """
    Altera o Nome da Definição da Característica (`nmCaracteristica`) e confirma UMA vez.

    Convenção vigente: uma única confirmação (ao salvar, a tela pode recarregar e limpar os
    dados, o que quebraria um segundo submit) e alteração do Nome sempre por ADIÇÃO de sufixo
    (" ALT"/" TLA"), mantendo o registro localizável pela Consulta e o teste re-executável.
    Não mexe em checkbox/radio (Tabelado, Unicidade, Bloqueio ficam intactos).

    Cenário A. Pressupõe que o registro já foi carregado (ver `selecionar_definicao_caracteristica`).
    """
    logger.info("Iniciou alteração da Definição da Característica.")

    ctx = escopo(page)
    campo = ctx.locator("input[name='nmCaracteristica']")
    logger.info("Alterando o Nome da Definição da Característica: '{}' -> '{}'.", campo.input_value(), proximo_nome(campo.input_value()))
    campo.fill(proximo_nome(campo.input_value()))

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou alteração da Definição da Característica.")
