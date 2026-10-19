from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global
from flows.shared.selecionar_movimentacao_flow import selecionar_movimentacao


def selecionar_funcionario(page: Page, funcionario: dict) -> bool:
    """
    Anexa o registro de Funcionário usando o auxiliar compartilhado `selecionar_movimentacao`
    (aguarda o total do banco em `span[name='searchResultSize']`). Casa a linha pelo Nome
    (coluna exibida no grid). Cenário A. Pressupõe consulta já feita.

    :return: True se encontrado e anexado; False caso contrário.
    """
    logger.info("Iniciou seleção de Funcionário '{}'.", funcionario["matricula"])

    ctx = escopo(page)

    if not selecionar_movimentacao(ctx, funcionario["nome"]):
        logger.info("Nenhum registro encontrado para '{}'.", funcionario["nome"])
        ctx.locator("button[name='submitCancel']").click()
        aguardar_ajax_global(page)
        return False

    logger.info("Finalizou seleção de Funcionário. Filtrado pelo campo de Nome: '{}'.", funcionario["nome"])
    return True
