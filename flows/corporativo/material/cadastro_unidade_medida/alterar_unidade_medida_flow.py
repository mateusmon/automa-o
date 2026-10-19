from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def alterar_unidade_medida(page: Page) -> None:
    """
    Altera a Descrição da Unidade de Medida (`dsUm`) e confirma UMA vez (sem desfazer).

    Convenção vigente: uma única confirmação (ao salvar, a tela pode recarregar e limpar os
    dados, o que quebraria um segundo submit). Aqui a alteração NÃO é por adição de sufixo
    porque o campo tem `maxlength` (acrescentar estouraria o limite e a Consulta casa pela
    Sigla, não pela Descrição): troca-se o último caractere, alternando X <-> Y — mudança
    real, idempotente e limitada. Não mexe em checkbox/radio. Cenário A. Pressupõe o registro
    já carregado (ver `selecionar_unidade_medida`).
    """
    logger.info("Iniciou alteração de Unidade de Medida.")

    ctx = escopo(page)
    campo = ctx.locator("input[name='dsUm']")
    atual = campo.input_value()
    # O campo tem maxlength; não dá para acrescentar sufixo. Alterna o último caractere.
    modificado = atual[:-1] + ("X" if atual[-1:] != "X" else "Y")
    campo.fill(modificado)

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou alteração de Unidade de Medida.")
