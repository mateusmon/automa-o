from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, proximo_nome


def alterar_funcao(page: Page) -> None:
    """
    Altera o Nome de Função (`nmTpFuncaoHier`) e confirma UMA vez (sem desfazer).

    Convenção vigente: uma única confirmação (ao salvar, a tela pode recarregar e limpar os
    dados, o que quebraria um segundo submit) e alteração do Nome sempre por ADIÇÃO de sufixo
    (" ALT"/" TLA"), mantendo o registro localizável pela Consulta e o teste re-executável.
    Não mexe em checkbox/radio. Cenário A. Pressupõe o registro já carregado (ver `selecionar_funcao`).
    """
    ctx = escopo(page)
    logger.info(
        "Iniciou alteração de Função '{}'.",
        ctx.locator("input[name='nmTpFuncaoHier']").input_value(),
    )

    campo = ctx.locator("input[name='nmTpFuncaoHier']")
    logger.info(
        "Alterando o Nome de Função: '{}' -> '{}'.",
        campo.input_value(),
        proximo_nome(campo.input_value()),
    )
    campo.fill(proximo_nome(campo.input_value()))

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info(
        "Finalizou alteração de Função'{}'.",
        ctx.locator("input[name='nmTpFuncaoHier']").input_value(),
    )
