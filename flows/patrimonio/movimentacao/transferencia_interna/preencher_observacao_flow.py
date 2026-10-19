from loguru import logger
from playwright.sync_api import Page, expect

from utils.competencia_financeira import obter_data_patrimonio
from utils.versao import escopo
from utils.waits import clicar_com_ajax, proximo_nome


def preencher_observacao(page: Page) -> None:
    logger.info("Iniciou preenchimento da observação.")

    ctx = escopo(page)

    data = obter_data_patrimonio(page)

    clicar_com_ajax(ctx, "button[name='submitTabObservacoes']")

    # Verificação dos botões
    clicar_com_ajax(ctx, "button[name='submitAddLine1']")

    ctx.locator("textarea[name='dsObs']").fill("OBSERVAÇÃO TESTE...")

    clicar_com_ajax(ctx, "button[name='submitRestore']")

    clicar_com_ajax(ctx, "button[name='submitCancel']")

    clicar_com_ajax(ctx, "button[name='submitAddLine1']")

    ctx.locator("input[name='dtObs']").fill(data)

    select = ctx.locator("select[name='tipoObs']")

    for opcao in select.locator("option").all():
        valor = opcao.get_attribute("value")

        select.select_option(valor)

        expect(select).to_have_value(valor)

    ctx.locator("textarea[name='dsObs']").fill("OBSERVAÇÃO TESTE...")

    clicar_com_ajax(ctx, "button[name='submitBack']")

    linhas = ctx.locator("table.tabela tbody tr")

    if linhas.count() == 0:
        logger.warning("A adição da observação não foi feita. Verificar manualmente.")
        botao_return = ctx.locator("button[name='submitBack']")

        clicar_com_ajax(ctx, botao_return)
        clicar_com_ajax(ctx, botao_return)

    btn_editar = linhas.nth(0).locator("td").nth(5).locator("button").last

    clicar_com_ajax(ctx, btn_editar)

    opcao = select.locator("option").first.get_attribute("value")
    select.select_option(opcao)
    observacao_input = ctx.locator("textarea[name='dsObs']")
    observacao_input.fill(proximo_nome(observacao_input.input_value()))

    valor_select = select.locator("option:checked").inner_text()

    clicar_com_ajax(ctx, "button[name='submitBack']")

    if valor_select != ctx.locator("td[name='observacoes-1-5']").inner_text():
        logger.warning("A observação não foi editada corretamente.")

    clicar_com_ajax(ctx, "button[name='submitBack']")
    clicar_com_ajax(ctx, "button[name='submitBack']")

    logger.info("Finalizou preenchimento da observação.")