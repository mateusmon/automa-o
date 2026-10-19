from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_almoxarifado
from utils.geradores import gerar_nf_por_data, gerar_numero_com_digitos
from utils.versao import escopo


def preencher_documentos(page: Page) -> None:
    logger.info("Iniciou preenchimento da tabela 'Documentos'.")

    ctx = escopo(page)

    linhas = ctx.locator("tbody[name='tboItensDoc'] tr")
    total_linhas = linhas.count()

    if total_linhas <= 0:
        logger.info("Preenchimento de documentos não é necessário para esta modalidade.")
        return

    data_hoje = obter_data_almoxarifado(page, "DDMMYYYY")

    for i in range(total_linhas):
        linha = linhas.nth(i)

        tipo = linha.locator("td").nth(1).locator("select")
        texto_tipo = tipo.evaluate("el => el.options[el.selectedIndex].text").strip()

        input_numero = linha.locator("td").nth(2).locator("input[type='text']")
        input_data = linha.locator("td").nth(3).locator("input[type='text']").first

        if texto_tipo == "NOTA FISCAL":
            logger.info("Preenchendo número da nota fiscal.")
            input_numero.type(gerar_nf_por_data(), delay=50)
        else:
            max_length = input_numero.get_attribute("maxlength")
            logger.info("Preenchendo número do documento.")
            input_numero.type(gerar_numero_com_digitos(int(max_length) if max_length else 10), delay=50)

        logger.info("Preenchendo data do documento: {}.", data_hoje)
        input_data.type(data_hoje, delay=50)

    logger.info("Finalizou preenchimento da tabela 'Documentos'.")
