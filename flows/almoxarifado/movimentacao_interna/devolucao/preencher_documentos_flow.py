from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_almoxarifado
from utils.geradores import gerar_numero_com_digitos, gerar_processo_sei
from utils.versao import escopo


def preencher_documentos(page: Page) -> None:
    logger.info("Iniciou preenchimento de documentos da devolução.")

    ctx = escopo(page)
    linhas_docs = ctx.locator("tbody[name='tboDocumentos'] tr")
    total_docs = linhas_docs.count()

    if total_docs <= 0:
        logger.info("Nenhum documento adicional para preencher.")
        return

    data_hoje = obter_data_almoxarifado(page, "DDMMYYYY")

    for i in range(total_docs):
        linha = linhas_docs.nth(i)

        tipo_elem = linha.locator("td").nth(1).locator("select")
        texto_tipo = ""
        if tipo_elem.count() > 0:
            texto_tipo = tipo_elem.evaluate("el => el.options[el.selectedIndex]?.text || ''").strip().upper()

        input_numero = linha.locator("td").nth(2).locator("input[type='text']")
        input_data = linha.locator("td").nth(3).locator("input[type='text']").first

        if input_numero.count() > 0 and input_numero.is_visible() and input_numero.input_value() == "":
            max_length = input_numero.get_attribute("maxlength")
            max_length_int = int(max_length) if max_length else 10

            if "SEI" in texto_tipo:
                numero_gerado = gerar_processo_sei()
            else:
                numero_gerado = gerar_numero_com_digitos(max_length_int)

            logger.info("Preenchendo número do documento: '{}'.", numero_gerado[-max_length_int:])
            input_numero.click()
            input_numero.type(numero_gerado[-max_length_int:], delay=50)

        if (
            input_data.count() > 0
            and input_data.is_visible()
            and input_data.is_enabled()
            and input_data.input_value() == ""
        ):
            logger.info("Preenchendo data do documento: '{}'.", data_hoje)
            input_data.click()
            input_data.type(data_hoje, delay=50)

    logger.info("Finalizou preenchimento de documentos da devolução.")
