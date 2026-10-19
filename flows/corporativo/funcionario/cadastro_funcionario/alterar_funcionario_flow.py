from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, proximo_nome


def alterar_funcionario(page: Page) -> None:
    """
    Altera o Nome/Registro Civil do Funcionário (`nmRegistroCivil`) e confirma UMA vez.

    Convenção vigente: uma única confirmação (ao salvar, a tela pode recarregar e limpar os
    dados, o que quebraria um segundo submit) e alteração do Nome sempre por ADIÇÃO de sufixo
    (" ALT"/" TLA"), mantendo o registro localizável pela Consulta (que filtra pelo CPF) e o
    teste re-executável. A U.A. é opcional, então não precisa ser re-selecionada. Não mexe em
    checkbox/radio. Cenário A. Pressupõe o registro já carregado (ver `selecionar_funcionario`).
    """
    logger.info("Iniciou alteração de Funcionário.")

    ctx = escopo(page)
    campo = ctx.locator("input[name='nmRegistroCivil']")
    logger.info("Alterando o Nome/Registro Civil do Funcionário: '{}' -> '{}'.", campo.input_value(), proximo_nome(campo.input_value()))
    campo.fill(proximo_nome(campo.input_value()))

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou alteração de Funcionário.")
