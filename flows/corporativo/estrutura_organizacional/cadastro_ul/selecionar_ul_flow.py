from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global
from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao


def selecionar_ul(page: Page, ul: dict) -> bool:
    """
    Anexa o registro de UL - Unidade de Localização usando o auxiliar compartilhado
    `selecionar_movimentacao`, que aguarda o total de itens vindo do banco
    (`span[name='searchResultSize']`) antes de decidir.
    Cenário A. Pressupõe que a consulta já foi feita (filtro pela Sigla).

    ⚠️ Casa a linha pelo **Endereço**, não pela Sigla: o grid de resultado da UL mostra
    Órgão / Responsável / Corresponsável / U.G. / U.A. / Código / Endereço — **não há coluna
    Sigla nem Nome** (confirmado ao vivo). O Endereço serve como discriminador porque a
    `unidade_localizacao_cr` usa um endereço dedicado, não utilizado por nenhuma outra UL.

    :param ul: dict do blueprint (usa a chave `endereco`).
    :return: True se o registro foi encontrado e anexado; False caso contrário.
    """
    logger.info("Iniciou seleção de UL - Unidade de Localização: '{}'.", ul["endereco"])

    ctx = escopo(page)

    if not selecionar_movimentacao(ctx, ul["endereco"]):
        logger.info("Nenhum registro encontrado para '{}'.", ul["endereco"])
        ctx.locator("button[name='submitCancel']").click()
        aguardar_ajax_global(page)
        return False

    logger.info("Finalizou seleção de UL - Unidade de Localização: '{}'.", ul["endereco"])
    return True
