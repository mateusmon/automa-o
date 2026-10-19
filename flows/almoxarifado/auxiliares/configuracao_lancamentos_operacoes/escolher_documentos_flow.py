from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro


def escolher_documentos(page: Page) -> None:
    logger.info("Iniciou escolha de documentos.")

    ctx = escopo(page)

    for _ in range(3):
        ctx.locator("button[name='submitAddLine1']").click()
        aguardar_ajax_global(page)

    logger.info("Selecionando primeiro tipo de documento.")
    ctx.select_option("select[name='cdTpDocumento-1-2']", value="001")
    aguardar_ajax_global(page)
    logger.info("Selecionando segundo tipo de documento.")
    ctx.select_option("select[name='cdTpDocumento-2-2']", value="002")
    aguardar_ajax_global(page)
    logger.info("Selecionando terceiro tipo de documento.")
    ctx.select_option("select[name='cdTpDocumento-3-2']", value="003")
    aguardar_ajax_global(page)

    for n in range(3):
        logger.info("Preenchendo Quantidade Máxima de Ocorrências '50'.")
        ctx.locator(f"input[name='qtMaxOcorrencias-{n+1}-7']").fill("50")
        logger.info("Preenchendo Quantidade Fixa de Ocorrências '1'.")
        ctx.locator(f"input[name='qtFixaOcorrencias-{n+1}-8']").fill("1")
        aguardar_ajax_global(page)

    logger.info("Finalizou escolha de documentos.")

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)