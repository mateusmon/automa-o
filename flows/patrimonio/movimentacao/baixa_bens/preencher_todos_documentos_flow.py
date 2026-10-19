from loguru import logger
from playwright.sync_api import Page, expect

from utils.competencia_financeira import obter_data_patrimonio
from utils.geradores import gerar_numero_com_digitos
from utils.versao import escopo
from utils.waits import (
    aguardar_ajax_global,
    clicar_com_ajax,
    preencher_campo,
)


def preencher_todos_documentos(page: Page) -> None:
    ctx = escopo(page)
    logger.info("Iniciou preenchimento de todos os documentos na tabela.")

    _page = page

    linhas = ctx.locator("tbody tr[model^='model-']")
    expect(linhas.first).to_be_visible()

    total_inicial = linhas.count()

    # 1. Adiciona e valida aumento
    clicar_com_ajax(ctx, ctx.locator("button[name='submitAddDocumento']"))
    total_apos_adicionar = linhas.count()

    if total_apos_adicionar <= total_inicial:
        raise AssertionError(
            f"Falha ao adicionar: esperava mais de {total_inicial} linhas, mas obtive {total_apos_adicionar}."
        )

    # 2. Exclui e valida diminuição
    clicar_com_ajax(ctx, ctx.locator("button[name='submitPurgeDocumentos']"))
    total_apos_remover = linhas.count()

    if total_apos_remover >= total_apos_adicionar:
        raise AssertionError(
            f"Falha ao remover: esperava menos de {total_apos_adicionar} linhas, mas obtive {total_apos_remover}."
        )

    data_hoje = obter_data_patrimonio(page, "DDMMYYYY")
    logger.info(f"Data obtida: {data_hoje}")

    clicar_com_ajax(ctx, ctx.locator("button[name='submitAddDocumento']"))
    total_apos_adicionar = linhas.count()
    for i in range(total_apos_adicionar):
        linha = linhas.nth(i)

        input_numero = linha.locator("input[bind='nrDocumento']").first
        input_data = linha.locator("input[bind='dtEmissao']").first
        input_emitente = linha.locator("input[bind='agente']").first
        input_contato = linha.locator("input[bind='nmContato']").first

        if not input_numero.is_enabled():
            logger.info(f"Linha {i + 1} desabilitada. Pulando...")
            continue

        max_length_contato = int(input_contato.get_attribute("maxlength") or 10)
        numero_gerado = gerar_numero_com_digitos(max_length_contato)

        # 1. Campo Número (lookup padrão: lookup-nrDocumento-X-Y)
        preencher_campo(ctx, input_numero, "   ")

        # 2. Campo Data
        input_data.click()
        logger.info(f"Preenchendo campo de data na linha {i + 1} com: {data_hoje}")
        input_data.fill("")
        input_data.type(data_hoje, delay=50)
        aguardar_ajax_global(_page)

        # 3. Campo Emitente (passa o lookup_name explicitamente por causa do prefixo lookup-documentos-)
        input_emitente_name = input_emitente.get_attribute("name")
        # Converte 'agente-1-6' -> 'lookup-documentos-1-6'
        lookup_emitente = input_emitente_name.replace("agente-", "lookup-documentos-")

        preencher_campo(ctx, input_emitente, "   ", lookup_name=lookup_emitente)

        # 4. Campo Contato
        input_contato.click()
        input_contato.type(numero_gerado[-max_length_contato:], delay=50)
        aguardar_ajax_global(_page)

    logger.info("Finalizou preenchimento de todos os documentos na tabela.")
