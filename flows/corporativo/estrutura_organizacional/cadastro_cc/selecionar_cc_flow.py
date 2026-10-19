from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global
from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao


def selecionar_cc(page: Page, centro_custo: dict) -> bool:
    """
    Anexa o registro de CC - Centro de Custos usando o auxiliar compartilhado `selecionar_movimentacao`,
    que aguarda o total de itens vindo do banco (`span[name='searchResultSize']`) antes de
    decidir — evita o falso-negativo de contar as linhas antes de a busca retornar.
    Cenário A. Pressupõe que a consulta já foi feita (filtro pela chave `nome`).

    Casa a linha pelo **Nome** (coluna sempre exibida no grid de resultado); a Sigla nem
    sempre é uma coluna visível (ex.: UA mostra Órgão/UG/Código/Nome/Responsável).

    :param centro_custo: dict do blueprint (usa a chave `nome`).
    :return: True se o registro foi encontrado e anexado; False caso contrário.
    """
    logger.info("Iniciou seleção de CC - Centro de Custos filtrado pelo Nome: '{}'.", centro_custo["nome"])

    ctx = escopo(page)

    if not selecionar_movimentacao(ctx, centro_custo["nome"]):
        logger.info("Nenhum registro encontrado para '{}'.", centro_custo["nome"])
        ctx.locator("button[name='submitCancel']").click()
        aguardar_ajax_global(page)
        return False

    logger.info("Finalizou seleção de CC - Centro de Custos. Filtrado pelo Nome: '{}'.", centro_custo["nome"])
    return True
