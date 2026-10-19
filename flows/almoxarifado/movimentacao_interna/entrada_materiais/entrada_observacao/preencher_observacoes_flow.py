from loguru import logger
from playwright.sync_api import Page, expect

from utils.competencia_financeira import obter_data_almoxarifado
from utils.versao import escopo
from utils.waits import aguardar_ajax_global, clicar_com_ajax


def preencher_observacoes(page: Page, material: dict) -> None:
    logger.info("Iniciou o preenchimento da aba 'Observações' para o material '{}'.", material["nome"])

    ctx = escopo(page)

    clicar_com_ajax(ctx, ctx.get_by_role("button", name="Observações"))

    ctx.locator('button[name="submitAddLine"]').click()
    expect(ctx.get_by_role("list").filter(has_text="Edição")).to_be_visible()
    aguardar_ajax_global(page)

    data_hoje = obter_data_almoxarifado(page, formato="DDMMYYYY")

    logger.info("Preenchendo data de observação: '{}'.", data_hoje)
    data_input = ctx.locator('input[name="dtObs"]')
    data_input.clear()
    data_input.type(data_hoje, delay=50)

    logger.info("Preenchendo observação: '{}'.", material["observacao"])
    ctx.locator('textarea[name="dsObs"]').type(material["observacao"], delay=50)

    ctx.get_by_role("button", name="Retornar").click()
    expect(ctx.locator('input[name="observacoes-1-1"]')).to_be_visible()

    botao_materiais = ctx.get_by_role("button", name="Materiais")

    clicar_com_ajax(ctx, botao_materiais)

    logger.info("Finalizou o preenchimento da aba 'Observações'.")
