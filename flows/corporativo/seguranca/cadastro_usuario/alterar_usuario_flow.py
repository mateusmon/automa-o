from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


_EMAIL_ALT = "usuario.cr.alterado@automacao.gov.br"


def alterar_usuario(page: Page, usuario: dict) -> None:
    """
    Altera o Usuário e confirma UMA vez (sem desfazer). Cenário A.

    O Usuário NÃO tem campo Nome — a identidade é o funcionário (campo desabilitado ao
    carregar). Por isso a convenção do sufixo no nome não se aplica. A alteração mexe apenas
    no campo seguro e não-chave **E-mail** (`nmEmail`), alternando entre o e-mail do blueprint
    e um alternativo (`_EMAIL_ALT`) — mudança real a cada execução e re-executável, ambos
    e-mails válidos. **NÃO** re-preenche a Senha: confirmado ao vivo que re-informar a mesma
    senha faz o Confirmar dar erro (a senha em branco mantém a atual). Não mexe em
    checkbox/radio nem no grid de sistemas/perfis. Escolha definida por inspeção ao vivo (o
    Usuário não tem outro campo de texto livre alterável com segurança).

    Pressupõe que o registro já foi carregado (ver `selecionar_usuario`).

    :param usuario: dict do blueprint (`funcionario_usuario_cr`): usa `email`.
    """
    logger.info("Iniciou alteração de Usuário.")

    ctx = escopo(page)

    campo = ctx.locator("input[name='nmEmail']")
    atual = campo.input_value().strip().lower()
    logger.info("Alterando o E-mail do Usuário: '{}' -> '{}'.", atual, usuario["email"] if atual == _EMAIL_ALT else _EMAIL_ALT)
    campo.fill(usuario["email"] if atual == _EMAIL_ALT else _EMAIL_ALT)

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou alteração de Usuário.")
