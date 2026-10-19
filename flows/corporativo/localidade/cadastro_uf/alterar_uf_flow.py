from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, proximo_nome


def alterar_uf(page: Page) -> None:
    """
    Altera o Nome de UF - Unidade da Federação (`nmUf`) e confirma UMA vez (sem desfazer).

    Convenção vigente: uma única confirmação (ao salvar, a tela pode recarregar e limpar os
    dados, o que quebraria um segundo submit) e alteração do Nome sempre por ADIÇÃO de sufixo
    (" ALT"/" TLA"), mantendo o registro localizável pela Consulta e o teste re-executável.
    Não mexe em checkbox/radio. Cenário A. Pressupõe o registro já carregado (ver `selecionar_uf`).
    """
    logger.info("Iniciou alteração de UF - Unidade da Federação.")

    ctx = escopo(page)
    campo = ctx.locator("input[name='nmUf']")
    campo.fill(proximo_nome(campo.input_value()))
    logger.info("Alterando o Nome de UF - Unidade da Federação: '{}' -> '{}'.", campo.input_value(), proximo_nome(campo.input_value()))
    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou alteração de UF - Unidade da Federação.")
