from loguru import logger
from playwright.sync_api import Page

from flows.genesis.shared.preencher_lookup_flow import preencher_campo
from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def consultar_perfis_por_usuario(page: Page, nome_usuario: str) -> None:
    """
    Abre a Consulta de Perfil e filtra pelo Usuário (`model-3`, lookup), deixando a
    grid de resultados aberta — mesma sequência de `_consultar_perfis` do legado
    `remover_restricoes_perfis_flow`. Diferente de `consultar_perfis_do_usuario`,
    não cancela nem lê a grid: o chamador abre as linhas a partir dela.

    :param nome_usuario: Nome do usuário usado como filtro.
    """
    logger.info("Consultando perfis do usuário '{}'.", nome_usuario)

    ctx = escopo(page)

    ctx.get_by_role("button", name="Consulta", exact=True).click()
    aguardar_ajax_global(page)

    preencher_campo(ctx, "input[name='model-3']", nome_usuario)
    ctx.get_by_title("Consultar novo registro").click()
    aguardar_ajax_global(page)
