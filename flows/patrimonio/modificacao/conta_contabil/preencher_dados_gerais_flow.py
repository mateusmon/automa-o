import random
import re

from loguru import logger
from playwright.sync_api import Frame, Page, expect

from utils.versao import escopo
from utils.waits import (
    aguardar_ajax_global,
    clicar_com_ajax,
    esperar_sucesso_ou_erro,
    preencher_campo,
)


def preencher_dados_gerais(page: Page, bem: dict[str, str]) -> None:
    logger.info("Iniciou preenchimento de dados gerais do bem '{}'.", bem["nome"])

    ctx = escopo(page)
    nome_completo_bem = f"{bem['nome']} {bem['complemento']}"

    preencher_campo(ctx, "input[name='bemServico']", nome_completo_bem)
    try:
        expect(ctx.locator("input[name='bemServico']")).to_have_value(re.compile(r"^\d+\s*-\s*[A-Z0-9]+\s+.+$"))
    except AssertionError:
        logger.warning("Falha ao buscar bem: {}", bem['nome'])

    escolher_conta_contabil(ctx, page)

    ctx.locator("button[name='submitFinish']").click()
    aguardar_ajax_global(page)
    esperar_sucesso_ou_erro(ctx)

    logger.info("Finalizou preenchimento de dados gerais do bem '{}'.", bem["nome"])


def escolher_conta_contabil(ctx: Page | Frame, page: Page) -> None:

    conta_atual = ctx.locator("input[name='conta']").input_value().strip().split(" - ", 1)[0]
    
    clicar_com_ajax(ctx, "button[name='lookup-contaDestino']")
    aguardar_ajax_global(page)
    
    clicar_com_ajax(ctx, "button[name='submitSearch']")
    aguardar_ajax_global(page)

    linhas = (
        ctx.locator("table[name='paginationTable'] tbody tr")
        .filter(has_not_text=conta_atual)
        .filter(has_not_text="ESTOQUE")
    )
    linhas.first.wait_for(state="visible")

    count = linhas.count()

    if count == 0:
        raise ValueError("Nenhuma conta disponível.")

    linha = linhas.nth(random.randrange(count))
    botao = linha.locator("button[name='submitUse']")
    clicar_com_ajax(ctx, botao)
