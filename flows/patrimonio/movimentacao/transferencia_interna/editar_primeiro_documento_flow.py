from loguru import logger
from playwright.sync_api import Page

from utils.geradores import gerar_email, gerar_numero_com_digitos
from utils.versao import escopo
from utils.waits import clicar_com_ajax, preencher_campo


def editar_primeiro_documento(page: Page, fornecedor: dict[str, str]) -> None:
    logger.info("Iniciou a edição do primeiro documento.")

    ctx = escopo(page)

    linhas = ctx.locator("table.tabela tbody tr")

    if linhas.count() == 0:
        logger.warning("Nenhum documento disponível. Pulando flow.")
        return

    botao_acoes = linhas.nth(0).locator("td").nth(7).locator("button")

    clicar_com_ajax(ctx, botao_acoes)

    # Verificar botões Restaurar e Cancelar
    input_numero = ctx.locator("input[name='nrDocumento']")
    numero_antigo = input_numero.input_value()

    max_length = input_numero.get_attribute("maxlength")
    max_length = int(max_length) if max_length else 10

    novo_numero = gerar_numero_com_digitos(max_length)

    ctx.locator("input[name='nrDocumento']").fill(novo_numero)
    clicar_com_ajax(ctx, "button[name='submitRestore']")

    # Verificar se a página foi Restaurada
    if numero_antigo != novo_numero:
        logger.warning("O botão 'Restaurar' não funcionou.")

    clicar_com_ajax(ctx, "button[name='submitCancel']")

    clicar_com_ajax(ctx, botao_acoes)

    # Modifica os campos do documento
    input_agente = ctx.locator("input[name='agente']")
    input_contato = ctx.locator("input[name='nmContato']")

    novo_contato = gerar_email()

    input_numero.fill(novo_numero)
    preencher_campo(ctx, input_agente, fornecedor["nome"])
    input_contato.fill(novo_contato)

    logger.info("Finalizou a edição do primeiro documento.")
