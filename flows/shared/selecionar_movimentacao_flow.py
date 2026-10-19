from typing import Literal

from loguru import logger
from playwright.sync_api import Frame, Page, expect

from utils.versao import escopo
from utils.waits import aguardar_ajax_global


def selecionar_movimentacao(
    page: Page | Frame,
    texto: str,
    table_locator: str = "table[name='paginationTable'] tbody tr",
    posicao: Literal["first", "last"] = "first",
) -> bool:
    """
    Seleciona uma movimentação na tabela de resultados e clica no botão
    "Anexar" da linha correspondente ao texto informado.

    A função procura pelas linhas da tabela que contenham o texto recebido
    e seleciona a primeira ou a última ocorrência encontrada, de acordo com
    o parâmetro `posicao`.

    Args:
        page: Instância da página do Playwright.
        texto: Texto utilizado para localizar a movimentação desejada.
        table_locator: Locator das linhas da tabela de resultados.
        posicao:
            - "first": seleciona a primeira ocorrência encontrada.
            - "last": seleciona a última ocorrência encontrada.

    Returns:
        True se a movimentação foi encontrada e anexada.
        False caso nenhuma movimentação correspondente seja localizada.
    """

    # Separando page e frame
    if isinstance(page, Page):
        ctx = escopo(page)
    else:
        ctx = page
        page = ctx.page

    # Esse span apresenta o total de itens consultados
    span_resultado = ctx.locator("span[name='searchResultSize']")
    span_resultado.wait_for(state="visible")

    if span_resultado.inner_text() == "0":
        logger.debug("Total de itens consultados: {}", span_resultado.inner_text())
        return False

    table = table_locator.split(" ", 1)[0]
    expect(
        ctx.locator(table), f"Erro ao encontrar tabela {table_locator}."
    ).to_be_visible(timeout=15_000)

    rows = ctx.locator(table_locator)

    # IMPORTANTE: este helper compartilhado seleciona por SUBSTRING de propósito.
    # Muitos flows dependem de ``has_text`` e dos modos first/last; não trocar esta
    # comparação por igualdade exata/normalizada nem criar exceção para Genesis.
    # Os pilotos Genesis precisam tratar identidade, acentuação e duplicidade em um
    # auxiliar próprio em flows/genesis/shared (ver Sprint 1 do PLANO_SPRINTS.md).
    # Pegando a primeira movimentação
    if posicao == "first":
        linha = rows.filter(has_text=texto).first
        if linha.count() == 0:
            # Checa caso tenha somente uma movimentação, que já entra direto, sem opção de seleção
            linha.locator("button[name='submitUse']").click()
            aguardar_ajax_global(page)
            return ctx.locator(f"text={texto}").count() > 0

    # Pegando a última movimentação
    if posicao == "last":
        linha = rows.filter(has_text=texto).last
        if linha.count() == 0:
            # Checa caso tenha somente uma movimentação, que já entra direto, sem opção de seleção
            linha.locator("button[name='submitUse']").click()
            aguardar_ajax_global(page)
            return ctx.locator(f"text={texto}").count() > 0

    linha.locator("button[name='submitUse']").click()
    aguardar_ajax_global(page)
    return True
