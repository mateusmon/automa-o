from loguru import logger
from playwright.sync_api import Page

from utils.geradores import gerar_pdf_temporario
from utils.versao import escopo
from utils.waits import clicar_com_ajax


def editar_primeiro_documento_com_anexo(
    page: Page,
    descricao_anexo: str = "DOCUMENTO PDF AUTOMATIZADO"
) -> None:
    logger.info("Iniciou a edição do primeiro documento.")

    ctx = escopo(page)

    # Gera sempre o arquivo PDF dinâmico
    arquivo_path = gerar_pdf_temporario()
    logger.info(f"PDF temporário gerado dinamicamente em: {arquivo_path}")

    # 1. Abertura do primeiro documento
    logger.info("Abrindo tela de edição do primeiro documento...")
    btn_editar = ctx.locator("tbody[name='tboItens'] tr:nth-child(1) button[title='Editar']")
    clicar_com_ajax(ctx, btn_editar)

    # 2. Grade de Arquivos e Descrição
    logger.info("Acessando a grade de arquivos...")
    primeira_linha_arquivo = ctx.locator("table tbody tr").first
    
    campo_desc = primeira_linha_arquivo.locator("input[type='text']").first
    if campo_desc.is_visible():
        logger.info(f"Preenchendo descrição: {descricao_anexo}")
        campo_desc.fill(descricao_anexo)

    # 3. Clica no botão de Anexar Arquivo para associar a linha
    btn_anexar_acao = primeira_linha_arquivo.locator("button[name^='edit-observacoes-1-5']")
    
    if btn_anexar_acao.is_visible():
        logger.info("Clicando no botão 'Anexar Arquivo' para associar a linha...")
        clicar_com_ajax(ctx, btn_anexar_acao)

    # 4. Upload do PDF no input file
    logger.info(f"Injetando arquivo PDF no input file: {arquivo_path}")
    input_file = ctx.locator("input[name='arquivo'][type='file']").first
    input_file.set_input_files(str(arquivo_path))

    # 5. Retorno à tela principal
    clicar_com_ajax(ctx, "button[name='submitBack']")
    clicar_com_ajax(ctx, "button[name='submitBack']")
    logger.info("Finalizou a edição do primeiro documento com anexo PDF.")