from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import aguardar_ajax_global, esperar_sucesso_ou_erro, preencher_campo

def desfazer_movimento(page: Page, endereco: str) -> None:
    logger.info("Desfazendo movimento do endereço '{}'.", endereco)

    ctx = escopo(page)

    ctx.locator("button[name='submitAddLine1']").click()
    aguardar_ajax_global(page)

    endereco = endereco.split(" - ", 1)[1].strip()

    logger.info("Preenchendo endereço '{}'.", endereco)
    preencher_campo(ctx, "input[name='endereco-2-3']", endereco)
    logger.info("Preenchendo UM 'UMT'.")
    preencher_campo(ctx, "input[name='um-2-4']", "UMT")
    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)