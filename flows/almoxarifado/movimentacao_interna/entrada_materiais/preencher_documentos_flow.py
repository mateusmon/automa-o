from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_almoxarifado
from utils.geradores import gerar_nf_por_data, gerar_numero_com_digitos
from utils.versao import escopo


def preencher_documentos(page: Page):
    logger.info("Iniciando preenchimento da tabela 'Documentos'.")

    ctx = escopo(page)
    linhas = ctx.locator("tbody[name='tboDocumentos'] tr")

    total_linhas = linhas.count()
    data_hoje = obter_data_almoxarifado(page, "DDMMYYYY")

    for i in range(total_linhas):
        linha = linhas.nth(i)

        checkbox = linha.locator("td").nth(0).locator("input[type='checkbox']")
        tipo = linha.locator("td").nth(1).locator("select")

        if checkbox.is_disabled():
            input_numero = linha.locator("td").nth(2).locator("input[type='text']")
            
            max_length = input_numero.get_attribute("maxlength")
            max_length = int(max_length) if max_length else 10
            
            if tipo.input_value() != "003":    
                numero_gerado = gerar_numero_com_digitos(max_length)
            else:
                numero_gerado = gerar_nf_por_data()

            logger.info("Preenchendo número do documento: '{}'.", numero_gerado[-max_length:])
            input_numero.type(numero_gerado[-max_length:], delay=50)

            logger.info("Preenchendo data do documento: '{}'.", data_hoje)
            input_data = linha.locator("td").nth(3).locator("input[type='text']").first
            input_data.type(data_hoje, delay=50)
    logger.info("Finalizando o preenchimento da tabela 'Documentos'.")
