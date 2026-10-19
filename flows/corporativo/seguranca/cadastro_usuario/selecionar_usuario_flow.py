from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def selecionar_usuario(page: Page, usuario: dict) -> bool:
    """
    Anexa o Usuário do funcionário consultado. Cenário A. Pressupõe que a consulta já foi feita.

    A Consulta já filtra pelo funcionário (lookup), então o resultado tem no máximo UMA linha
    (um funcionário tem um usuário) — por isso seleciona a primeira linha. O nome do funcionário
    vem MASCARADO no grid (`matrícula - *****`), então não dá para casar pelo nome; usa-se o
    total do banco (`span[name='searchResultSize']`) como guarda e pega a 1ª linha.

    :param usuario: dict do blueprint (não usado além de manter a assinatura padrão).
    :return: True se encontrou e anexou; False caso contrário.
    """
    logger.info("Iniciou seleção de Usuário '{}'.", usuario["nome"])

    ctx = escopo(page)

    span = ctx.locator("span[name='searchResultSize']")
    try:
        span.wait_for(state="visible", timeout=10_000)
    except Exception:
        logger.info("Nenhum resultado de consulta de Usuário (funcionário inexistente): '{}'.", usuario["nome"])
        return False

    if span.inner_text() == "0":
        logger.info("Nenhum usuário encontrado para o funcionário '{}'.", usuario["nome"])
        ctx.locator("button[name='submitCancel']").click()
        aguardar_ajax_global(page)
        return False

    ctx.locator("table[name='paginationTable'] tbody tr:first-child button[name='submitUse']").click()
    aguardar_ajax_global(page)

    logger.info("Finalizou seleção de Usuário '{}'.", usuario["nome"])
    return True
