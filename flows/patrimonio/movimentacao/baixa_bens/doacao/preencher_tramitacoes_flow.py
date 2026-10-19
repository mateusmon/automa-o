from loguru import logger
from playwright.sync_api import Page

from utils.competencia_financeira import obter_data_patrimonio
from utils.versao import escopo
from utils.waits import (
    aguardar_ajax_global,
    clicar_com_ajax,
    preencher_campo,
)


def preencher_tramitacoes(page: Page, usuario: dict) -> None:
    logger.info("Iniciando preenchimento da aba Tramitações.")
    ctx = escopo(page)

    # 1. Acessa a aba Tramitações caso não esteja nela
    aba_tramitacoes = ctx.locator("button[name='submitTabTramitacoes']").first
    if aba_tramitacoes.is_visible():
        clicar_com_ajax(ctx, aba_tramitacoes)

    # 2. Selecionar Roteiro Padrão (se existir opção válida)
    select_roteiro = ctx.locator(
        "select[name='roteiroPadrao'], select[bind='roteiroPadrao']"
    ).first
    if select_roteiro.is_visible():
        options = select_roteiro.locator("option").all()
        opcoes_validas = [
            opt.get_attribute("value") for opt in options if opt.get_attribute("value")
        ]
        if opcoes_validas:
            logger.info(f"Selecionando roteiro padrão: {opcoes_validas[0]}")
            select_roteiro.select_option(value=opcoes_validas[0])
            aguardar_ajax_global(page)

    # Locators da tabela de tramitação
    linhas = ctx.locator("tr[model^='model-']")
    btn_add = ctx.locator("button[name='submitAddLine1']").first
    btn_purge = ctx.locator("button[name='submitPurgeLines1']").first

    # 3. Esquema: Adicionar -> Remover -> Adicionar
    total_inicial = linhas.count()

    # Adicionar
    if btn_add.is_visible():
        clicar_com_ajax(ctx, btn_add)
        total_add1 = linhas.count()
        if total_add1 <= total_inicial:
            logger.warning(
                f"Falha ao adicionar linha: esperava > {total_inicial}, veio {total_add1}"
            )
    else:
        total_add1 = total_inicial

    # Remover
    if btn_purge.is_visible():
        clicar_com_ajax(ctx, btn_purge)
        total_purge = linhas.count()
        if total_purge >= total_add1:
            logger.warning(
                f"Falha ao remover linha: esperava < {total_add1}, veio {total_purge}"
            )
    else:
        total_purge = total_add1

    # Adicionar novamente
    if btn_add.is_visible():
        clicar_com_ajax(ctx, btn_add)
        total_add2 = linhas.count()
        if total_add2 <= total_purge:
            logger.warning(
                f"Falha ao adicionar linha novamente: esperava > {total_purge}, veio {total_add2}"
            )

    # 4. Preenchimento de Todas as Linhas
    data_hoje = obter_data_patrimonio(page, "DDMMYYYY")
    nome_responsavel = usuario.get("nome", "RAFAEL AUTOMAÇÃO DE CAMPOS")
    qtd_linhas = linhas.count()

    logger.info(f"Iniciando o preenchimento de {qtd_linhas} linha(s) na tabela.")

    for idx in range(qtd_linhas):
        linha_atual = linhas.nth(idx)

        # Campo Data (bind="dtTramitacao")
        input_data = linha_atual.locator("input[bind='dtTramitacao']").first
        if input_data.is_visible():
            input_data.click()
            input_data.fill("")
            input_data.type(data_hoje, delay=50)
            aguardar_ajax_global(page)

        # Campo Tarefa (bind="dsTramitacao")
        input_tarefa = linha_atual.locator("input[bind='dsTramitacao']").first
        if input_tarefa.is_visible():
            input_tarefa.fill(f"TRAMITAÇÃO AUTOMATIZADA {idx + 1}")

        # Campo Responsável (bind="funcionario") e Lupa
        input_responsavel = linha_atual.locator("input[bind='funcionario']").first

        if input_responsavel.is_visible():
            preencher_campo(ctx, input_responsavel, nome_responsavel)

    logger.info("Preenchimento da aba Tramitações finalizado com sucesso.")
