"""Consulta dos Perfis associados ao usuário autenticado."""

from loguru import logger
from playwright.sync_api import Page

from flows.genesis.shared.filtrar_perfis_usuario_flow import (
    filtrar_perfis_por_usuario,
)
from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_perfis_do_usuario(page: Page, nome_usuario: str) -> list[dict]:
    """Consulta e retorna os Perfis associados ao usuário informado.

    A consulta é fechada antes do retorno. Apenas as linhas visíveis são
    devolvidas, preservando o comportamento do Genesis legado diante de paginação.

    :param page: Página principal do ASI.
    :param nome_usuario: Nome exibido para o usuário autenticado.
    :return: Lista com ``codigo``, ``nome`` e ``sistema`` de cada Perfil.
    """
    logger.info("Iniciou consulta dos Perfis do usuário '{}'.", nome_usuario)

    ctx = escopo(page)
    ctx.locator("button[name='submitSearch']").click()
    aguardar_ajax_global(page)
    filtrar_perfis_por_usuario(page, ctx, nome_usuario)

    resultado = ctx.locator("span[name='searchResultSize']")
    resultado.wait_for(state="visible")
    total = int(resultado.inner_text().strip())
    perfis: list[dict] = []

    if total > 0:
        linhas = ctx.locator("table[name='paginationTable'] tbody tr")
        linhas_visiveis = linhas.count()
        if linhas_visiveis != total:
            logger.warning(
                "A consulta informou {} Perfis, mas exibiu {} linhas; apenas as "
                "linhas visíveis serão consideradas.",
                total,
                linhas_visiveis,
            )
        for indice in range(linhas_visiveis):
            linha = linhas.nth(indice)
            perfis.append(
                {
                    "codigo": linha.locator("td[columnid='1']").inner_text().strip(),
                    "nome": linha.locator("td[columnid='2']").inner_text().strip(),
                    "sistema": linha.locator("td[columnid='3']").inner_text().strip(),
                }
            )

    ctx.locator("button[name='submitCancel']").click()
    aguardar_ajax_global(page)
    logger.info("Finalizou consulta dos Perfis do usuário '{}'.", nome_usuario)
    return perfis
