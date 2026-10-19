from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global
from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao


def selecionar_ur(page: Page, unidade_requisicao: dict) -> bool:
    """
    Anexa o registro de UR - Unidade de Requisição usando o auxiliar compartilhado `selecionar_movimentacao`,
    que aguarda o total de itens vindo do banco (`span[name='searchResultSize']`) antes de
    decidir — evita o falso-negativo de contar as linhas antes de a busca retornar.
    Cenário A. Pressupõe que a consulta já foi feita (filtro pela chave `nome`).

    Casa a linha pelo **Nome** (coluna sempre exibida no grid de resultado); a Sigla nem
    sempre é uma coluna visível (ex.: UA mostra Órgão/UG/Código/Nome/Responsável).

    :param unidade_requisicao: dict do blueprint (usa a chave `nome`).
    :return: True se o registro foi encontrado e anexado; False caso contrário.
    """
    logger.info("Iniciou seleção de UR - Unidade de Requisição: '{}'.", unidade_requisicao["nome"])

    ctx = escopo(page)

    if not selecionar_movimentacao(ctx, unidade_requisicao["nome"]):
        logger.info("Nenhum registro encontrado para '{}'.", unidade_requisicao["nome"])
        ctx.locator("button[name='submitCancel']").click()
        aguardar_ajax_global(page)
        return False

    logger.info("Finalizou seleção de UR - Unidade de Requisição: '{}'.", unidade_requisicao["nome"])
    return True
