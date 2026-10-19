from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo


def contar_perfis_consultados(page: Page) -> int:
    """
    Retorna quantos Perfis a consulta atual exibiu, pela mesma regra do legado
    (`_remover_restricoes`): 0 se o total do banco for "0" ou se a página de
    resultado não for alcançada; caso contrário, o número de linhas da grid.
    """
    ctx = escopo(page)
    try:
        # Esse span é populado pelo banco e é a fonte confiável do total de resultados
        span_resultado = ctx.locator("span[name='searchResultSize']")
        span_resultado.wait_for(state="visible")

        if span_resultado.inner_text() == "0":
            logger.info("Não há perfis para este usuário.")
            return 0
    except Exception:
        logger.info("Erro inesperado. Provavelmente não chegou à página de resultado de consulta de perfis.")
        return 0

    tabela = ctx.locator("table[name='paginationTable']")
    tabela.wait_for(state="visible")

    total_perfis = tabela.locator("tbody tr").count()
    logger.info("Encontrado(s) {} perfil(is) para processar.", total_perfis)
    return total_perfis
