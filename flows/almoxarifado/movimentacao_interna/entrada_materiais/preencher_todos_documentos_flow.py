
from loguru import logger
from playwright.sync_api import Page, expect

from utils.competencia_financeira import obter_data_almoxarifado
from utils.geradores import gerar_nf_por_data, gerar_numero_com_digitos
from utils.versao import escopo


def preencher_todos_documentos(page: Page) -> None:
    logger.info("Iniciou preenchimento de todos os documentos na tabela.")

    ctx = escopo(page)
    linhas = ctx.locator("tbody[name='tboDocumentos'] tr")
    expect(linhas.first).to_be_visible()

    total_linhas = linhas.count()
    data_hoje = obter_data_almoxarifado(page, "DDMMYYYY")

    for i in range(total_linhas):
        linha = linhas.nth(i)

        tipo = linha.locator("td").nth(1).locator("select")
        input_numero = linha.locator("td").nth(2).locator("input[type='text']")
        input_data = linha.locator("td").nth(3).locator("input[type='text']").first

        max_length = input_numero.get_attribute("maxlength")
        max_length = int(max_length) if max_length else 10

        if tipo.input_value() != "003":
            numero_gerado = gerar_numero_com_digitos(max_length)
        else:
            numero_gerado = gerar_nf_por_data()

        # Garante o foco e realiza a digitação em cada linha
        logger.info("Preenchendo número do documento '{}': '{}'.", i, numero_gerado[-max_length:])
        input_numero.click()
        input_numero.type(numero_gerado[-max_length:], delay=50)

        logger.info("Preenchendo data do documento '{}': '{}'.", i, data_hoje)    
        input_data.click()
        input_data.type(data_hoje, delay=50)

    logger.info("Finalizou preenchimento de todos os documentos na tabela.")
