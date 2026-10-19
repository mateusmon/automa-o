from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, proximo_nome



def alterar_instalacao(page: Page) -> None:
    """
    Altera o Bairro da Instalação (`nmBairro`) e confirma UMA vez (sem desfazer).

    Convenção vigente: uma única confirmação (ao salvar, a tela pode recarregar e limpar os
    dados, o que quebraria um segundo submit) e alteração por ADIÇÃO de sufixo (" ALT"/" TLA").
    Altera-se o Bairro (texto livre, sem lookup) e não o Nome porque o Nome depende do lookup
    de Cidade — defeituoso na v4 (ao Anexar, o botão só reinicia a página em vez de puxar o
    valor); mexer só no Bairro não revalida a Cidade. A Consulta filtra pelo Nome, então o
    Bairro não a afeta. Não mexe em checkbox/radio. Cenário A. Pressupõe o registro já
    carregado (ver `selecionar_instalacao`).
    """
    logger.info("Iniciou alteração de Instalação.")

    ctx = escopo(page)
    campo = ctx.locator("input[name='nmBairro']")
    logger.info("Alterando o Bairro da Instalação: '{}' -> '{}'.", campo.input_value(), proximo_nome(campo.input_value()))
    campo.fill(proximo_nome(campo.input_value()))

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou alteração de Instalação.")
