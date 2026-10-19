from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, proximo_nome


def alterar_ul(page: Page) -> None:
    """
    Altera a Sigla da UL - Unidade de Localização (`sgUl`) e confirma UMA vez (sem desfazer).

    Convenção vigente: uma única confirmação (ao salvar, a tela pode recarregar e limpar os
    dados, o que quebraria um segundo submit) e alteração por ADIÇÃO de sufixo (" ALT"/" TLA").
    A UL **não tem campo Nome** — a Sigla é o único campo de texto livre equivalente. Alterá-la
    é seguro porque a chave única da UL é (U.A., Endereço), não a Sigla; e a Consulta filtra a
    Sigla por conteúdo, então o valor-base continua localizando o registro. Não mexe em
    checkbox/radio (`inContabilizacao`, `inIntervencao`, `inBloqueio` ficam intactos).

    Cenário A. Pressupõe que o registro já foi carregado (ver `selecionar_ul`).
    """
    ctx = escopo(page)
    campo = ctx.locator("input[name='sgUl']")
    logger.info(
        "Iniciou alteração de UL - Unidade de Localização: '{}'.", campo.input_value()
    )

    logger.info(
        "Alterando a Sigla de UL - Unidade de Localização: '{}' -> '{}'.",
        campo.input_value(),
        proximo_nome(campo.input_value()),
    )
    campo.fill(proximo_nome(campo.input_value()))

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info(
        "Finalizou alteração de UL - Unidade de Localização: '{}'.", campo.input_value()
    )
