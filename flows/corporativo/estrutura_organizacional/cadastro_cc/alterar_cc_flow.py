from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, proximo_nome


def alterar_cc(page: Page) -> bool:
    """
    Altera o Nome do CC - Centro de Custos (`nmCentroCusto`) e confirma UMA vez (sem desfazer).

    Convenção vigente: uma única confirmação (ao salvar, a tela pode recarregar e limpar os
    dados, o que quebraria um segundo submit) e alteração do Nome sempre por ADIÇÃO de sufixo
    (" ALT"/" TLA"), mantendo o registro localizável pela Consulta e o teste re-executável.
    Não mexe em checkbox/radio. Cenário A. Pressupõe o registro já carregado (ver `selecionar_cc`).

    Se o botão "Confirmar" (`submitFinish`) estiver desabilitado após o preenchimento do Nome,
    a alteração é considerada inviável nesta execução: o flow loga e retorna `False` sem tentar
    o clique (evita o timeout do Playwright, que aguardaria o botão ficar habilitado antes de
    clicar). Vale para qualquer cliente.

    :return: True se a alteração foi confirmada; False se o botão de confirmar estava desabilitado (alteração inviável nesta execução).
    """
    ctx = escopo(page)
    logger.info(
        "Iniciou alteração de CC - Centro de Custos '{}'.",
        ctx.locator("input[name='nmCentroCusto']").input_value(),
    )

    campo = ctx.locator("input[name='nmCentroCusto']")
    logger.info(
        "Alterando o Nome do CC - Centro de Custos: '{}' -> '{}'.",
        campo.input_value(),
        proximo_nome(campo.input_value()),
    )
    campo.fill(proximo_nome(campo.input_value()))

    botao_confirmar = ctx.locator("button[name='submitFinish']")

    if botao_confirmar.is_disabled():
        logger.warning("Botão de confirmar desabilitado. Alteração Inviável.")
        return False

    botao_confirmar.click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info(
        "Finalizou alteração de CC - Centro de Custos '{}'.",
        ctx.locator("input[name='nmCentroCusto']").input_value(),
    )

    return True
