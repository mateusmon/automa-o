from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_patrimonio
from utils.geradores import gerar_numero_com_digitos
from utils.versao import escopo
from utils.waits import preencher_campo


def preencher_documentos_associados(page: Page, fornecedor: dict[str, str]) -> bool:
    logger.info("Iniciou preenchimento de documentos associados.")

    ctx = escopo(page)

    linhas = ctx.locator("tbody tr").filter(has=ctx.locator("input[bind='nrDocumento']"))

    if linhas.count() == 0:
        logger.info("Nenhum documento associado encontrado.")
        return False

    data_hoje = obter_data_patrimonio(page, formato="DDMMYYYY")

    for i in range(linhas.count()):
        linha = linhas.nth(i)

        campo_numero = linha.locator("input[bind='nrDocumento']").first
        if campo_numero.is_visible() and campo_numero.is_editable():
            logger.info("Preenchendo número do documento associado na linha '{}'.", i + 1)
            max_length = campo_numero.get_attribute("maxlength")
            limite = int(max_length) if max_length else 10
            campo_numero.fill(gerar_numero_com_digitos(limite))

        campo_data = linha.locator("input[bind='dtEmissao']").first
        if campo_data.is_visible() and campo_data.is_editable():
            logger.info("Preenchendo data do documento associado na linha '{}'.", i + 1)
            campo_data.type(data_hoje, delay=50)

        campo_emitente = linha.locator("input[bind='agente']").first
        if campo_emitente.is_visible() and campo_emitente.is_editable():
            logger.info("Preenchendo emitente do documento associado na linha '{}' com fornecedor '{}'.", i + 1, fornecedor["nome"])
            preencher_campo(ctx, campo_emitente, fornecedor["nome"])

        campo_contato = linha.locator("input[bind='nmContato']").first
        if campo_contato.is_visible() and campo_contato.is_editable():
            logger.info("Preenchendo contato do documento associado na linha '{}'.", i + 1)
            max_length = campo_contato.get_attribute("maxlength")
            limite = int(max_length) if max_length else 10
            campo_contato.fill(gerar_numero_com_digitos(limite))

    logger.info("Finalizou preenchimento de documentos associados.")
    return True