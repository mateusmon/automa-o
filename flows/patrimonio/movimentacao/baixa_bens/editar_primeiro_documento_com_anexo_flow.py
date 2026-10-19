from pathlib import Path

from loguru import logger
from playwright.sync_api import Page, expect

from utils.geradores import gerar_pdf_temporario
from utils.versao import escopo
from utils.waits import clicar_com_ajax


def editar_primeiro_documento_com_anexo(
    page: Page,
    caminho_imagem: str | Path | None = None,
    descricao_anexo: str = "IMAGEM AUTOMATIZADA",
) -> None:
    logger.info("Iniciou a edição do primeiro documento.")

    ctx = escopo(page)

    if caminho_imagem is None:
        arquivo_path = gerar_pdf_temporario()
        logger.info("PDF temporário gerado dinamicamente em: '{}'.", arquivo_path)
    else:
        arquivo_path = Path(caminho_imagem)

    # 1. Abertura do primeiro documento habilitado
    logger.info("Abrindo tela de edição do primeiro documento.")
    btn_editar = ctx.locator("button[name^='edit-documentos-']").first
    clicar_com_ajax(ctx, btn_editar)

    # Locators da tabela interna de arquivos
    linhas_tabela = ctx.locator("table tbody tr")
    btn_add_linha = ctx.locator("button[name='submitAddLine1']")
    btn_purge_linha = ctx.locator("button[name='submitPurgeLines1']")

    expect(linhas_tabela.first).to_be_visible()

    # 2. Esquema: acrescentar -> diminuir -> acrescentar linhas
    total_inicial = linhas_tabela.count()

    # Passos de alteração e checagens com IF / ELSE
    clicar_com_ajax(ctx, btn_add_linha)
    total_apos_add1 = linhas_tabela.count()
    if total_apos_add1 <= total_inicial:
        raise AssertionError(
            f"Falha no 1º add: esperava > {total_inicial}, veio {total_apos_add1}"
        )

    clicar_com_ajax(ctx, btn_purge_linha)
    total_apos_purge = linhas_tabela.count()
    if total_apos_purge >= total_apos_add1:
        raise AssertionError(
            f"Falha no purge: esperava < {total_apos_add1}, veio {total_apos_purge}"
        )

    clicar_com_ajax(ctx, btn_add_linha)
    total_apos_add2 = linhas_tabela.count()
    if total_apos_add2 <= total_apos_purge:
        raise AssertionError(
            f"Falha no 2º add: esperava > {total_apos_purge}, veio {total_apos_add2}"
        )

    # 3. Grade de Arquivos e Preenchimento da Descrição
    logger.info("Acessando a grade de arquivos.")
    primeira_linha_arquivo = linhas_tabela.first

    campo_desc = primeira_linha_arquivo.locator("input[type='text']").first
    if campo_desc.is_visible():
        logger.info("Preenchendo descrição: '{}'.", descricao_anexo)
        campo_desc.fill(descricao_anexo)

    # 4. Clica no botão de Anexar Arquivo da linha
    btn_anexar_acao = primeira_linha_arquivo.locator(
        "button[name^='edit-observacoes-']"
    )
    if btn_anexar_acao.is_visible():
        logger.info("Clicando no botão 'Anexar Arquivo' para associar a linha.")
        clicar_com_ajax(ctx, btn_anexar_acao.first)

    # 5. Upload do arquivo
    logger.info("Injetando arquivo no input file: '{}'.", arquivo_path)
    input_file = ctx.locator("input[name='arquivo'][type='file']").first
    input_file.set_input_files(str(arquivo_path))

    # 6. Confirmação do anexo clicando em 'Incluir'
    logger.info("Confirmando a inclusão do arquivo anexado.")
    btn_incluir = ctx.locator(
        "button[name='submitBack'], button[title='Incluir']:has-text('Incluir')"
    ).first
    clicar_com_ajax(ctx, btn_incluir)

    # 7. Retorno à tela principal
    clicar_com_ajax(ctx, "button:has-text('Retornar')")
    logger.info("Finalizou a edição do primeiro documento.")
