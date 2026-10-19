from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global
from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao


def selecionar_unidade_medida(page: Page, unidade_medida: dict) -> bool:
    """
    Anexa o registro de Unidade de Medida usando o auxiliar compartilhado `selecionar_movimentacao`
    (aguarda o total do banco em `span[name='searchResultSize']`). Casa a linha pela
    Sigla (coluna exibida no grid; a Descrição é truncada no banco). Cenário A.
    Pressupõe consulta já feita.

    :return: True se encontrado e anexado; False caso contrário.
    """
    logger.info("Iniciou seleção de Unidade de Medida.")

    ctx = escopo(page)

    if not selecionar_movimentacao(ctx, unidade_medida["sigla"]):
        logger.info("Nenhum registro encontrado para '{}'.", unidade_medida["sigla"])
        ctx.locator("button[name='submitCancel']").click()
        aguardar_ajax_global(page)
        return False

    logger.info("Finalizou seleção de Unidade de Medida.")
    return True
