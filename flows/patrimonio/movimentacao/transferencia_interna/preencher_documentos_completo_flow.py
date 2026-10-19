
from loguru import logger
from playwright.sync_api import Page, expect

from utils.competencia_financeira import obter_data_patrimonio
from utils.geradores import gerar_email, gerar_numero_com_digitos
from utils.versao import escopo
from utils.waits import clicar_com_ajax, preencher_campo


def preencher_documentos(page: Page, fornecedor_padrao: dict[str, str]) -> bool:
    logger.info("Iniciou o preenchimento de documentos completo.")

    ctx = escopo(page)

    # Pegue todas as linhas da tabela
    linhas = ctx.locator("table.tabela tbody tr")
    total_linhas = linhas.count()

    if total_linhas == 0 and ctx.locator("button[name='submitAddDocumento']").is_disabled():
        logger.warning("Nenhum documento disponível. Pulando flow.")
        return False

    data = obter_data_patrimonio(page)

    # Verificar botão de adicionar e subtrair linhas
    input_emitente = linhas.nth(0).locator("td").nth(5).locator("input[type='text']")
    preencher_campo(ctx,input_emitente, fornecedor_padrao["nome"])
    clicar_com_ajax(ctx, "input[name='submitMarkAll1']")
    clicar_com_ajax(ctx, "button[name='submitPurgeDocumentos']")

    total_linhas_remocao = linhas.count()
    if total_linhas_remocao == total_linhas:
        logger.warning("Erro na exclusão de linha.")

    clicar_com_ajax(ctx, "button[name='submitAddDocumento']")

    total_linhas_adicao = linhas.count()
    if total_linhas_adicao <= total_linhas_remocao:
        logger.warning("Erro ao adicionar linha.")

    total_linhas_preencher = linhas.count()

    # Verificar todos os tipos de documento
    ultimo_select = linhas.nth(total_linhas).locator("td").nth(2).locator("select")

    for opcao in ultimo_select.locator("option").all():
        valor = opcao.get_attribute("value")

        ultimo_select.select_option(valor)

        expect(ultimo_select).to_have_value(valor)

    for i in range(total_linhas_preencher):
        linha = linhas.nth(i)

        # input do número (quarta coluna)
        input_numero = linha.locator("td").nth(3).locator("input[type='text']")

        max_length = input_numero.get_attribute("maxlength")
        max_length = int(max_length) if max_length else 10

        numero_gerado = gerar_numero_com_digitos(max_length)
        input_numero.fill(numero_gerado)

        # input da data (quarta coluna)
        input_data = linha.locator("td").nth(4).locator("input[type='text']").first
        input_data.fill(data)

        # input Emitente
        emitente = linha.locator("td").nth(5).locator("input[type='text']")
        preencher_campo(ctx, emitente, fornecedor_padrao["nome"])

        # input Contato
        input_contato = linha.locator("td").nth(6).locator("input[type='text']")
        email_gerado = gerar_email()
        input_contato.fill(email_gerado)

    logger.info("Finalizou o preenchimento de documentos completo.")

    return True