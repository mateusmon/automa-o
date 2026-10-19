"""Filtro compartilhado da Consulta de Perfis pelo usuário associado."""

from playwright.sync_api import Frame, Page

from utils.waits import aguardar_ajax_global


def filtrar_perfis_por_usuario(
    page: Page, ctx: Page | Frame, nome_usuario: str
) -> None:
    """Resolve o lookup de Usuário e dispara a busca na Consulta de Perfis.

    :param page: Página principal, usada para sincronização AJAX.
    :param ctx: Escopo da tela de Perfil na versão ativa.
    :param nome_usuario: Nome exibido para o usuário autenticado.
    :raises RuntimeError: Quando o lookup apresenta alerta de erro ou aviso.
    """
    campo = ctx.locator("input[name='model-3']")
    campo.wait_for(state="visible")
    campo.fill(nome_usuario)
    ctx.locator("button[name='lookup-model-3']").click()
    aguardar_ajax_global(page)

    alerta = ctx.locator(".alert-danger, .alert-warning").first
    if alerta.is_visible():
        raise RuntimeError(
            f"A consulta de Perfis do usuário '{nome_usuario}' retornou: "
            f"{alerta.inner_text().strip()}"
        )

    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)
