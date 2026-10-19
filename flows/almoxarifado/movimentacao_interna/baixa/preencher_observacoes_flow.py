from loguru import logger
from playwright.sync_api import Page, expect

from utils.competencia_financeira import obter_data_almoxarifado
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, select_tipo


def preencher_observacoes(page: Page, finalidade: str | None = None) -> None:
    logger.info("Iniciou preenchimento da aba de observações da baixa.")

    ctx = escopo(page)

    botao_observacoes = ctx.locator("button[name='submitTabObservacoes']")

    if not botao_observacoes.is_visible():
        logger.warning("Aba de observações não visível.")
        return

    botao_observacoes.click()
    aguardar_ajax_global(page)
    ctx.locator("button[name='submitAddLine1']").click()
    aguardar_ajax_global(page)

    data_hoje = obter_data_almoxarifado(page, "DDMMYYYY")
    campo_data = ctx.locator("input[name='dtObs']")
    campo_data.clear()
    logger.info("Preenchendo data da observação com a data do almoxarifado: '{}'.", data_hoje)
    campo_data.type(data_hoje, delay=50)

    expect(ctx.locator("select[name='tipoObs']")).to_be_visible()
    if finalidade:
        logger.info("Selecionando finalidade da observação: '{}'.", finalidade)
        select_tipo(ctx, "tipoObs", finalidade)
        aguardar_ajax_global(page)
    logger.info("Preenchendo observação da baixa: 'Observação de Baixa Completa Automatizada'.")
    ctx.locator("textarea[name='dsObs']").fill("Observação de Baixa Completa Automatizada")
    ctx.locator("button[name='submitBack']").click()
    aguardar_ajax_global(page)

    botao_nota = ctx.locator("button[name='submitTabOrigem']")
    expect(botao_nota).to_be_visible()
    botao_nota.click()
    aguardar_ajax_global(page)

    logger.info("Finalizou preenchimento da aba de observações da baixa.")
