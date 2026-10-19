from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global
from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao


def selecionar_ug(page: Page, ug: dict) -> bool:
    """
    Anexa o registro de UG - Unidade Gestora usando o auxiliar compartilhado `selecionar_movimentacao`
    (aguarda o total do banco em `span[name='searchResultSize']`). Casa a linha pelo
    campo `nome` (coluna exibida no grid). Cenário A. Pressupõe consulta já feita.

    :return: True se encontrado e anexado; False caso contrário.
    """
    logger.info("Iniciou seleção de UG - Unidade Gestora: '{}'.", ug["codigo"])

    ctx = escopo(page)

    if not selecionar_movimentacao(ctx, ug["nome"]):
        logger.info("Nenhum registro encontrado para '{}'.", ug["nome"])
        ctx.locator("button[name='submitCancel']").click()
        aguardar_ajax_global(page)
        return False

    logger.info("Finalizou seleção de UG - Unidade Gestora: '{}'.", ug["codigo"])
    return True
