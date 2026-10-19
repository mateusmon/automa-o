from loguru import logger
from playwright.sync_api import Page, expect

from utils.competencia_financeira import obter_data_patrimonio
from utils.geradores import gerar_nf_por_data, gerar_numero_com_digitos
from utils.versao import escopo
from utils.waits import (
    aguardar_ajax_global,
    clicar_com_ajax,
)


def preencher_todos_documentos(page: Page, fornecedor: dict[str, str]) -> None:
    logger.info("Iniciou preenchimento de todos os documentos na tabela.")

    ctx = escopo(page)
    _page = page

    linhas = ctx.locator("tbody[name='tboItens'] tr")
    expect(linhas.first).to_be_visible()

    total_linhas = linhas.count()
    data_hoje = obter_data_patrimonio(page, "DDMMYYYY")
    logger.info(f"{data_hoje}")
    for i in range(total_linhas):
        linha = linhas.nth(i)

        tipo = linha.locator("select[bind='tipoDocumento']")
        input_numero = linha.locator("input[bind='nrDocumento']").first
        input_data = linha.locator("input[bind='dtEmissao']").first
        input_contato = linha.locator("input[bind='nmContato']").first
        btn_emitente = linha.locator("button[title='Consultar']").first

        max_length_num = input_numero.get_attribute("maxlength")
        max_length_num = int(max_length_num) if max_length_num else 10

        max_length_contato = input_contato.get_attribute("maxlength")
        max_length_contato = int(max_length_contato) if max_length_contato else 10

        if tipo.input_value() != "003":
            numero_gerado = gerar_numero_com_digitos(max_length_num)
        else:
            numero_gerado = gerar_nf_por_data()

        input_numero.click()
        input_numero.type(numero_gerado[-max_length_num:], delay=50)
        aguardar_ajax_global(_page)

        input_data.click()
        input_data.type(data_hoje, delay=50)
        aguardar_ajax_global(_page)

        clicar_com_ajax(ctx, btn_emitente)

        input_modal = ctx.locator("input[name='model-2']")
        input_modal.wait_for(state="visible")
        logger.info("Preenchendo campo de fornecedor com '{}'.", fornecedor["nome"])
        input_modal.fill(fornecedor["nome"])

        clicar_com_ajax(ctx, "button[name='submitSearch']")
        clicar_com_ajax(ctx, "button[name='submitUse']")

        input_contato.click()
        input_contato.type(numero_gerado[-max_length_contato:], delay=50)
        aguardar_ajax_global(_page)

    logger.info("Finalizou preenchimento de todos os documentos na tabela.")