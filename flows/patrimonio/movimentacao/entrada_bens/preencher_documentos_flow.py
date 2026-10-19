
from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_patrimonio
from utils.geradores import gerar_numero_com_digitos
from utils.versao import escopo


def preencher_documentos(page: Page) -> None:
    logger.info("Iniciou o preenchimento de documentos.")

    ctx = escopo(page)

    # Pegue todas as linhas da tabela
    linhas = ctx.locator("tbody[name='tboItens'] tr")
    total_linhas = linhas.count()

    data_hoje = obter_data_patrimonio(page, "DDMMYYYY")

    for i in range(total_linhas):
        linha = linhas.nth(i)

        # Checkbox da primeira coluna
        checkbox = linha.locator("td").nth(0).locator("input[type='checkbox']")

        # Se a checkbox estiver desabilitada, preencha a linha
        if checkbox.is_disabled():

            # input do número (terceira coluna)
            input_numero = linha.locator("td").nth(3).locator("input[type='text']")

            max_length = input_numero.get_attribute("maxlength")
            max_length = int(max_length) if max_length else 10

            numero_gerado = gerar_numero_com_digitos(max_length)
            logger.info("Preenchendo campo de Número do Documento com '{}'.", numero_gerado)
            input_numero.type(numero_gerado, delay=50)

            # input da data (quarta coluna)
            input_data = linha.locator("td").nth(4).locator("input[type='text']").first

            input_data.type(data_hoje, delay=50)

    logger.info("Finalizou o preenchimento de documentos.Total de linhas preenchidas: {}.", total_linhas)
