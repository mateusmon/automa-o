from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def selecionar_modelo_importacao(page: Page) -> bool:
    """
    Anexa o primeiro modelo do resultado da consulta, carregando-o no formulário
    (habilita o Excluir). Cenário A. Pressupõe que a consulta já foi feita.

    Escopa-se ao Anexar da primeira linha (`tr:first-child`) — o grid ext replica
    linhas ocultas de medição. Se não houver linha (consulta vazia), cancela e retorna
    False (nada a excluir).

    :return: True se um modelo foi encontrado e carregado; False caso contrário.
    """
    logger.info("Iniciou seleção de Modelo de Importação.")

    ctx = escopo(page)

    anexar = ctx.locator("table[name='paginationTable'] tbody tr:first-child button[name='submitUse']")

    if anexar.count() == 0:
        logger.info("Nenhum modelo encontrado.")
        ctx.locator("button[name='submitCancel']").click()
        aguardar_ajax_global(page)
        return False

    anexar.click()
    aguardar_ajax_global(page)

    logger.info("Finalizou seleção de Modelo de Importação.")
    return True
