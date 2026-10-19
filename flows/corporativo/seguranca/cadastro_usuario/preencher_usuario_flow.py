from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo


def preencher_usuario(page: Page, usuario: dict) -> None:
    """
    Cadastra o Usuário SOBRE um funcionário já existente e confirma. É o último flow da
    criação, então faz o submit (`submitFinish`) e aguarda o alerta. Cenário A.

    Pressupõe que o funcionário (`usuario["nome"]`) já foi criado (o teste cria o funcionário
    antes, reusando o flow de Funcionário). Sequência confirmada no Genesis
    (`garantir_usuarios/v4.py`): Funcionário (lookup) → Senha/Confirmação → para cada sistema:
    "Adicionar Linhas" → `sistemas-{i}-2` (nome do sistema) → `edit-sistemas-{i}-5` abre o
    sub-form de Perfil → `perfis-1-2` (perfil padrão, via `lookup-perfil-1-2`) →
    `cdPerfilSelecionado` → "Retornar". Ao final marca o `cdSistemaSelecionado` e confirma.

    :param usuario: dict do blueprint (`funcionario_usuario_cr`): nome, senha,
        sistemas[{nome, perfil}].
    """
    logger.info("Iniciou preenchimento de Usuário '{}'.", usuario["nome"])

    ctx = escopo(page)

    if ctx.locator("input[name='funcionario']").is_disabled():
        ctx.locator("button[name='submitNew']").click()
        aguardar_ajax_global(page)

    preencher_campo(ctx, "input[name='funcionario']", usuario["nome"])
    logger.info("Preenchendo campo de Funcionário do Usuário com '{}'.", usuario["nome"])
    ctx.locator("input[name='senha']").fill(usuario["senha"])
    logger.info("Preenchendo campo de Senha do Usuário com '{}'.", usuario["senha"])
    ctx.locator("input[name='confirmacaoSenha']").fill(usuario["senha"])

    for indice, sistema in enumerate(usuario["sistemas"], start=1):
        ctx.locator("button[name='submitAddLine1']").click()  # Adicionar Linhas
        aguardar_ajax_global(page)

        preencher_campo(ctx, f"input[name='sistemas-{indice}-2']", sistema["nome"])

        ctx.locator(f"button[name='edit-sistemas-{indice}-5']").click()  # abre o sub-form de Perfil
        aguardar_ajax_global(page)

        preencher_campo(ctx, "input[name='perfis-1-2']", sistema["perfil"], lookup_name="lookup-perfil-1-2")
        ctx.locator("input[name='cdPerfilSelecionado']").check()
        ctx.get_by_role("button", name="Retornar").click()
        aguardar_ajax_global(page)

    ctx.locator("input[name='cdSistemaSelecionado']").first.check()

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou preenchimento de Usuário '{}'.", usuario["nome"])
