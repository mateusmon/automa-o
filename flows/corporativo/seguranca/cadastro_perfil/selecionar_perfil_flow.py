from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global
from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao


def selecionar_perfil(page: Page, perfil: dict) -> bool:
    """
    Anexa o registro de Perfil usando o auxiliar compartilhado `selecionar_movimentacao`, que
    aguarda o total de itens vindo do banco (`span[name='searchResultSize']`) antes de decidir.
    Cenário A. Pressupõe que a consulta já foi feita (filtro pelo Nome).

    Casa a linha pelo **Nome** (o grid de resultado mostra Código / Nome / Sistema).

    :param perfil: dict do blueprint (usa a chave `nome`).
    :return: True se o registro foi encontrado e anexado; False caso contrário.
    """
    logger.info("Iniciou seleção de Perfil '{}'.", perfil["nome"])

    ctx = escopo(page)

    if not selecionar_movimentacao(ctx, perfil["nome"]):
        logger.info("Nenhum registro encontrado para '{}'.", perfil["nome"])
        ctx.locator("button[name='submitCancel']").click()
        aguardar_ajax_global(page)
        return False

    logger.info("Finalizou seleção de Perfil '{}'.", perfil["nome"])
    return True
