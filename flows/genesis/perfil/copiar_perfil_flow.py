"""Cópia integral de um Perfil de origem para o Genesis."""

from loguru import logger
from playwright.sync_api import Frame, Page

from flows.genesis.shared.filtrar_perfis_usuario_flow import (
    filtrar_perfis_por_usuario,
)
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, clicar_com_ajax


def copiar_perfil(
    page: Page,
    nome_usuario: str,
    perfil_origem: dict,
    nome_perfil: str,
) -> bool:
    """Copia integralmente um Perfil do usuário e confirma com um novo nome.

    :param page: Página principal do ASI, já posicionada em Perfil.
    :param nome_usuario: Usuário cujos Perfis serão consultados.
    :param perfil_origem: Registro com ``nome`` e ``sistema`` da origem.
    :param nome_perfil: Nome derivado que será atribuído à cópia.
    :return: ``False`` somente quando a cópia não apresentar módulos.
    """
    logger.info(
        "Iniciou cópia do Perfil '{}' para '{}'.",
        perfil_origem["nome"],
        nome_perfil,
    )

    ctx = escopo(page)
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)
    filtrar_perfis_por_usuario(page, ctx, nome_usuario)
    _anexar_origem(page, ctx, perfil_origem["nome"])

    clicar_com_ajax(ctx, ctx.get_by_role("button", name="Copiar perfil"))
    linhas_modulos = ctx.locator(
        "table.tabela:has(caption:text-is('Módulos')) tbody tr"
    )
    if linhas_modulos.count() == 0:
        logger.info(
            "Finalizou cópia sem criação: Perfil '{}' não apresentou módulos.",
            perfil_origem["nome"],
        )
        return False

    ctx.locator("input[name='nmPerfil']").fill(nome_perfil)
    aguardar_ajax_global(page)
    ctx.locator("button[name='submitFinish']").click(timeout=90_000)
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou cópia do Perfil para '{}'.", nome_perfil)
    return True

def _anexar_origem(
    page: Page, ctx: Page | Frame, nome_perfil_origem: str
) -> None:
    """Anexa a linha cujo Nome corresponde exatamente ao Perfil de origem."""
    linhas = ctx.locator("table[name='paginationTable'] tbody tr")
    linhas.first.wait_for(state="visible")
    for indice in range(linhas.count()):
        linha = linhas.nth(indice)
        nome = linha.locator("td[columnid='2']").inner_text().strip()
        if nome != nome_perfil_origem:
            continue
        clicar_com_ajax(ctx, linha.locator("button[name='submitUse']"))
        return

    raise RuntimeError(
        f"Perfil de origem '{nome_perfil_origem}' não encontrado na consulta por usuário."
    )
