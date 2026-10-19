from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import clicar_com_ajax


def verificar_modificacao_documento(page: Page, documento_original: dict[str, str]) -> None:
    logger.info("Iniciou verificação da modificação do documento.")

    ctx = escopo(page)

    clicar_com_ajax(ctx, "button[name='submitBack']")

    linhas = ctx.locator("table.tabela tbody tr")

    documento_atual = {
        "numero": linhas.nth(0).locator("td").nth(3).locator("input[type='text']").input_value(),
        "emitente": linhas.nth(0).locator("td").nth(5).locator("input[type='text']").input_value(),
        "contato": linhas.nth(0).locator("td").nth(6).locator("input[type='text']").input_value(),
    }

    if documento_original == documento_atual:
        logger.warning("Os dados da documentação não foram modificadas corretamente. Verificar manualmente.")

    logger.info("Finalizou verificação da modificação do documento.")
