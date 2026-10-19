import re

from loguru import logger
from playwright.sync_api import Page, expect

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def validar_botoes(page: Page) -> None:
    logger.info("Iniciou validação dos botões.")

    ctx = escopo(page)

    linhas_disponiveis = ctx.locator("table[name='paginationTable'] tbody tr")
    quantidade_para_adicionar = min(2, linhas_disponiveis.count())
    logger.info("Adicionando os {} primeiro(s) item(ns) disponível(eis).", quantidade_para_adicionar)
    for indice in range(quantidade_para_adicionar):
        linhas_disponiveis.nth(indice).locator("button[name='submitAdd']").click()
        aguardar_ajax_global(page)

    ctx.get_by_role("button", name="Adicionar itens").click()
    aguardar_ajax_global(page)

    ctx.get_by_role("button", name="Carregar todos").click()
    aguardar_ajax_global(page)

    celula_dt_requisicao = ctx.locator("table#itenstab td[bind='dtRequisicao']").first
    celula_dt_requisicao.click()

    # Valida se a célula recebeu a classe de foco após o clique
    expect(celula_dt_requisicao).to_have_class(re.compile(r"\btcFocusStyle\b"))

    ctx.locator('button[name="submitPrint"]').click()
    aguardar_ajax_global(page)

    ctx.locator('input[name="submitMarkAll1"]').click()
    aguardar_ajax_global(page)

    ctx.locator('button[name="submitPrint"]').click()
    aguardar_ajax_global(page)

    logger.success("Finalizou validação dos botões.")