from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global
from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao


def selecionar_definicao_caracteristica(page: Page, caracteristica: dict) -> bool:
    """
    Anexa o registro da Definição da Característica usando o auxiliar compartilhado
    `selecionar_movimentacao`, que aguarda o total de itens vindo do banco
    (`span[name='searchResultSize']`) antes de decidir.
    Cenário A. Pressupõe que a consulta já foi feita (filtro pelo Nome).

    Casa a linha pelo **Nome** (coluna "Nome da Característica", sempre exibida no grid).

    :param caracteristica: dict do blueprint (usa a chave `nome`).
    :return: True se o registro foi encontrado e anexado; False caso contrário.
    """
    logger.info("Iniciou seleção da Definição da Característica '{}'.", caracteristica["nome"])

    ctx = escopo(page)

    if not selecionar_movimentacao(ctx, caracteristica["nome"]):
        logger.info("Nenhum registro encontrado para '{}'.", caracteristica["nome"])
        ctx.locator("button[name='submitCancel']").click()
        aguardar_ajax_global(page)
        return False
    
    logger.info("Registro encontrado para '{}'.", caracteristica["nome"])
    logger.info("Finalizou seleção da Definição da Característica '{}'.", caracteristica["nome"])
    return True
