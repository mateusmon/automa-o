from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def preencher_parametros(page: Page) -> None:
    logger.info("Iniciou preenchimento de parâmetros de cadastro de ressuprimento.")

    ctx = escopo(page)
    _preencher(ctx, page)

    logger.info("Finalizou preenchimento de parâmetros de cadastro de ressuprimento.")


def _preencher(ctx, page: Page) -> None:
    rows = ctx.locator("table.tabela tbody tr")
    count = rows.count()

    if count == 1:
        logger.info("Preenchendo Lote de Compras '90'.")
        ctx.locator("input[name='ddLc-1-2']").fill("90")
        aguardar_ajax_global(page)
    else:
        raise RuntimeError("Já existem parâmetros cadastrados. Crie o código para esse caso.")