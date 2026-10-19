from loguru import logger
from playwright.sync_api import Page

from utils.versao import escopo
from utils.waits import clicar_com_ajax


def editar_documentos_associados(page: Page) -> None:
    logger.info("Iniciou edição de documentos associados.")

    ctx = escopo(page)

    botoes_editar = ctx.locator("tbody tr").filter(has=ctx.locator("input[bind='nrDocumento']")).locator("button[title='Editar']")

    for i in range(botoes_editar.count()):
        logger.info("Editando documento associado na linha '{}'.", i + 1)

        clicar_com_ajax(ctx, botoes_editar.nth(i))
        clicar_com_ajax(ctx, "button[name='lookup-agente']")
        clicar_com_ajax(ctx, "button[name='submitCancel']")
        clicar_com_ajax(ctx, "button[name='submitPurgeLines1']")
        clicar_com_ajax(ctx, "button[name='submitAddLine1']")

        logger.info("Preenchendo descrição do documento: 'DESCRIÇÃO DE DOCUMENTO ASSOCIADO AUTOMATIZADO'.")
        ctx.locator("input[bind='nmFantasia']").fill("DESCRIÇÃO DE DOCUMENTO ASSOCIADO AUTOMATIZADO")
        clicar_com_ajax(ctx, "button[name='submitBack']")

    logger.info("Finalizou edição de documentos associados.")