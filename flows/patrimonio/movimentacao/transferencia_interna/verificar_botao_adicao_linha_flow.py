from pathlib import Path

from loguru import logger
from playwright.sync_api import Page, expect

from utils.geradores import gerar_pdf_temporario
from utils.versao import escopo
from utils.waits import clicar_com_ajax


def verificar_botao_adicao_linha(
    page: Page, descricao_anexo: str, caminho_imagem: str | Path | None = None
) -> dict[str, str]:
    logger.info("Iniciou verificação do botão de Adição de linha.")

    ctx = escopo(page)

    documento_original = {
        "numero": ctx.locator("input[name='nrDocumento']").input_value(),
        "emitente": ctx.locator("input[name='agente']").input_value(),
        "contato": ctx.locator("input[name='nmContato']").input_value(),
    }

    linhas_arquivos = ctx.locator("table.tabela tbody tr")

    if linhas_arquivos.count() == 0 and ctx.locator("button[name='submitAddLine1']").is_disabled():
        logger.info("Finalizou verificação do botão de Adição de linha.")
        return documento_original
    elif linhas_arquivos.count() == 0:
        clicar_com_ajax(ctx, "button[name='submitAddLine1']")
        if linhas_arquivos.count() == 0:
            logger.warning("Botão de adição de linha não funcionou corretamente. Verificar manualmente")

    input_descricao = linhas_arquivos.nth(0).locator("td").nth(3).locator("input[type='text']")
    input_descricao.fill("ARQUIVO TESTE")

    _editar_documento_com_anexo(page, caminho_imagem, descricao_anexo)

    logger.info("Finalizou verificação do botão de Adição de linha.")
    return documento_original


def _editar_documento_com_anexo(page: Page, caminho_imagem: Path | str | None, descricao_anexo: str) -> None:
    logger.info("Iniciou edição do documento com anexo.")

    ctx = escopo(page)

    if caminho_imagem is None:
        arquivo_path = gerar_pdf_temporario()
        logger.debug(f"Imagem temporária gerada dinamicamente em : {arquivo_path}")
    else:
        arquivo_path = Path(caminho_imagem)

    # Anexando arquivo
    linhas = ctx.locator("table.tabela tbody tr")
    btn_anexar = linhas.nth(0).locator("td").nth(4).locator("button[name^='edit-observacoes-1-5']")

    if not btn_anexar.is_visible():
        logger.warning("Botão para anexar arquivo não encontrado.")
        return

    clicar_com_ajax(ctx, btn_anexar)
    clicar_com_ajax(ctx, "button[name='submitCancel']")
    clicar_com_ajax(ctx, btn_anexar)

    ctx.locator("input[name='nmFantasia']").fill(descricao_anexo)
    input_file = ctx.locator("input[name='arquivo'][type='file']").first
    input_file.set_input_files(str(arquivo_path))

    clicar_com_ajax(ctx, "button[name='submitBack']")

    expect(linhas.nth(0).locator("td").nth(2)).not_to_have_text("")

    logger.info("Finalizou edição do documento com anexo.")
