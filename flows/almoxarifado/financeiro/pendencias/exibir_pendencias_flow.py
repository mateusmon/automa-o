from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo


def exibir_pendencias(page: Page) -> None:
    logger.info("Iniciou exibição de pendências.")

    ctx = escopo(page)

    linhas = ctx.locator("table.tabela tbody tr")
    count_linhas = linhas.count()

    if count_linhas == 0:
        logger.info("Nenhuma pendência para esta UG.")
        return

    logger.warning("Veja as pendências: ")

    for n in range(count_linhas):
        ug_origem = linhas.nth(n).locator("td").nth(0).inner_text()
        almox_origem = linhas.nth(n).locator("td").nth(1).inner_text()
        ug_destino = linhas.nth(n).locator("td").nth(2).inner_text()
        almox_destino = linhas.nth(n).locator("td").nth(3).inner_text()

        logger.warning("UG Origem: '{}'", ug_origem)
        logger.warning("Almoxarifado Origem: '{}'", almox_origem)
        logger.warning("UG Destino: '{}'", ug_destino)
        logger.warning("Almoxarifado Destino: '{}'\n", almox_destino)

    page.wait_for_timeout(5_000)
    logger.info("Finalizou exibição de pendências.")
