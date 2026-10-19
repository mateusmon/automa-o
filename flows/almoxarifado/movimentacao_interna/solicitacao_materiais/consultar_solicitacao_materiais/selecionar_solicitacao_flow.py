from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def selecionar_solicitacao(page: Page, almoxarifado_data: dict[str, str]) -> bool:
    logger.info("Iniciou seleção de solicitação de materiais no almoxarifado '{}'.", almoxarifado_data["nome"])

    ctx = escopo(page)
    resultado = _selecionar(ctx, page, almoxarifado_data)

    logger.info("Finalizou seleção de solicitação de materiais no almoxarifado '{}'.", almoxarifado_data["nome"])
    return resultado


def _selecionar(ctx, page: Page, almoxarifado_data: dict[str, str]) -> bool:
    almoxarifado = almoxarifado_data["nome"]

    linha = ctx.locator("table[name='paginationTable'] tbody tr").filter(
        has=ctx.locator("td").nth(5).filter(has_text=almoxarifado)
    ).last

    if linha.count() == 0:
        logger.info("Nenhuma solicitação encontrada para o almoxarifado'{}'.", almoxarifado)
        return False

    logger.info("Foi encontrada uma solicitação para o almoxarifado '{}'.", almoxarifado)
    
    linha.locator("button[name='submitUse']").click()
    aguardar_ajax_global(page)

    return True
