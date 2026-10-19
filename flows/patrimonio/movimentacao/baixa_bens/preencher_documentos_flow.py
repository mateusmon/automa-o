from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_patrimonio
from utils.geradores import gerar_nf_por_data, gerar_numero_com_digitos
from utils.versao import escopo
from utils.waits import preencher_campo


def preencher_documentos(page: Page, fornecedor: dict[str, str]) -> None:
    logger.info("Iniciou preenchimento de Documentos.")

    ctx = escopo(page)

    # Pegue todas as linhas da tabela
    linhas = ctx.locator("table.tabela tbody tr")
    total_linhas = linhas.count()

    if linhas.count() <= 0:
        logger.info("Preenchimento de documentos não é necessário para esta modalidade.")
        return

    data_hoje = obter_data_patrimonio(page, "DDMMYYYY")

    for i in range(total_linhas):
        linha = linhas.nth(i)
        # Checkbox da primeira coluna
        checkbox = linha.locator("td").nth(0).locator("input[type='checkbox']")
        # Tipo de documento na segunda coluna
        tipo = linha.locator("td").nth(2).locator("select")

        # Se a checkbox estiver desabilitada, preencha a linha
        if checkbox.is_disabled():
            # Se o tipo de documento for diferente de nota fiscal, ele preenche a linha com a função gerar_numero_com_digitos 
            if tipo.input_value() != "003":
                # input do número (terceira coluna)
                input_numero = linha.locator("td").nth(3).locator("input[type='text']")
                max_length = input_numero.get_attribute("maxlength")
                max_length = int(max_length) if max_length else 10
                numero_gerado = gerar_numero_com_digitos(max_length)
                input_numero.type(numero_gerado, delay=50)
            else:
                # Se o tipo de documento for nota fiscal, ele preenche a linha com a função gerar_nf_por_data
                input_numero = linha.locator("td").nth(3).locator("input[type='text']")
                numero_gerado = gerar_nf_por_data()
                input_numero.type(numero_gerado, delay=50)

            # input da data (quarta coluna)
            input_data = linha.locator("td").nth(4).locator("input[type='text']").first
            input_data.type(data_hoje, delay=50)

            if linha.locator("td").nth(5).locator("input[type='text']").is_visible():
                # Campo de emitente (quinta coluna)
                campo_emitente = linha.locator("td").nth(5).locator("input[type='text']").first
                nome_emitente = campo_emitente.get_attribute("name")
                lookup_emitente = nome_emitente.replace("agente-", "lookup-documentos-")
                preencher_campo(ctx, campo_emitente, fornecedor["nome"], lookup_name=lookup_emitente)

    logger.info("Finalizou preenchimento de Documentos.")
