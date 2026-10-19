from pathlib import Path

from loguru import logger
from playwright.sync_api import Page

from utils.geradores import gerar_imagem_temporaria
from utils.versao import escopo
from utils.waits import clicar_com_ajax


def editar_primeiro_documento_com_anexo(page: Page, caminho_imagem: str | Path | None = None, descricao_anexo: str = "IMAGEM AUTOMATIZADA") -> None:
    logger.info("Iniciou a edição do primeiro documento.")

    ctx = escopo(page)

    # Resolve o caminho do arquivo (gera imagem temporária se nenhum caminho for fornecido)
    if caminho_imagem is None:
        arquivo_path = gerar_imagem_temporaria()
        logger.info("Imagem temporária gerada dinamicamente em: '{}'.", arquivo_path)
    else:
        arquivo_path = Path(caminho_imagem)

    # 1. Abertura do primeiro documento
    logger.info("Abrindo tela de edição do primeiro documento.")
    btn_editar = ctx.locator("tbody[name='tboDocumentos'] tr:nth-child(1) button[title='Editar']")
    clicar_com_ajax(ctx, btn_editar)

    # 2. Grade de Arquivos e Descrição
    logger.info("Acessando a grade de arquivos.")
    primeira_linha_arquivo = ctx.locator("table tbody tr").first
    
    campo_desc = primeira_linha_arquivo.locator("input[type='text']").first
    if campo_desc.is_visible():
        logger.info("Preenchendo descrição: '{}'.", descricao_anexo)
        campo_desc.fill(descricao_anexo)

    # 3. Clica no botão de Anexar Arquivo para associar a linha
    btn_anexar_acao = primeira_linha_arquivo.locator("button[name^='edit-itens-1-5']")
    
    if btn_anexar_acao.is_visible():
        logger.info("Clicando no botão 'Anexar Arquivo' para associar a linha.")
        clicar_com_ajax(ctx, btn_anexar_acao)

    # 4. Upload no input file
    logger.info("Injetando arquivo no input file: '{}'.", arquivo_path)
    input_file = ctx.locator("input[name='arquivo'][type='file']").first
    input_file.set_input_files(str(arquivo_path))

    # 5. Confirmação do anexo clicando em 'Incluir'
    logger.info("Confirmando a inclusão do arquivo anexado.")
    btn_incluir = ctx.locator("button[name='submitIncluir'], button[title='Incluir']:has-text('Incluir')").first
    clicar_com_ajax(ctx, btn_incluir)

    # 6. Retorno à tela principal
    clicar_com_ajax(ctx, "button:has-text('Retornar')")
    logger.info("Finalizou a edição do primeiro documento.")