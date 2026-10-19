from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, proximo_nome


def alterar_perfil(page: Page) -> None:
    """
    Altera o Nome do Perfil (`nmPerfil`) e confirma UMA vez (sem desfazer).

    Convenção vigente: uma única confirmação (ao salvar, a tela recarrega e limpa os dados,
    o que quebraria um segundo submit) e alteração do Nome sempre por ADIÇÃO de sufixo
    (" ALT"/" TLA"), mantendo o registro localizável pela Consulta e o teste re-executável.
    O Sistema fica desabilitado ao carregar (mantido) e o módulo é preservado. Não mexe em
    checkbox/radio (`bloqueado`, `inPerfilPadrao`).

    Cenário A. Pressupõe que o registro já foi carregado (ver `selecionar_perfil`).
    """
    logger.info("Iniciou alteração de Perfil.")

    ctx = escopo(page)
    campo = ctx.locator("input[name='nmPerfil']")
    campo.fill(proximo_nome(campo.input_value()))
    logger.info("Alterando o Nome do Perfil: '{}' -> '{}'.", campo.input_value(), proximo_nome(campo.input_value()))
    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou alteração de Perfil.")
