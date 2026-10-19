from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, clicar_com_ajax


def selecionar_requisicao(page: Page, ur: dict[str, str]) -> bool:
    """
    Seleciona para atendimento uma requisição da UR.
    """
    logger.info("Selecionando requisição para atendimento na UR '{}'.", ur["nome"])

    ctx = escopo(page)

    # Pega a última requisição que tenha a ur "PLANEJAMENTO ESTRATÉGICO INTEGRADO"
    logger.info("Localizando requisição para a UR '{}'.", ur["nome"])

    linha = ctx.locator("table.tabelaComRolagem tbody tr").last

    if linha.count() == 0:
        logger.warning("Nenhuma requisição encontrada para a UR {}.", ur["nome"])
        return False
    
    linha.last.locator("td").nth(8).locator("input[type='checkbox']").check()

    clicar_com_ajax(ctx, "button[name='submitTabAtendimento']")
    aguardar_ajax_global(page)

    logger.info("Requisição selecionada para atendimento na UR '{}'.", ur["nome"])
    return True
